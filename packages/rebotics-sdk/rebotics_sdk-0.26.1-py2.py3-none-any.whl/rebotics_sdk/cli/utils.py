import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Pool
from urllib.parse import urlparse, unquote

import click
import six
import tqdm
from click import get_current_context

from rebotics_sdk.cli.renderers import format_processing_action_output, format_full_table
from rebotics_sdk.utils import download_file
from ..advanced import remote_loaders
from ..providers import RetailerProvider
from ..utils import mkdir_p

if six.PY2:
    FileNotFoundError = IOError

app_dir = click.get_app_dir('rebotics-scripts')
try:
    mkdir_p(app_dir)
except PermissionError:
    logging.warning(
        "Failed to create click app directory. Please make sure that you have write access to the home directory"
    )


class DumpableConfiguration(object):
    def __init__(self, path):
        self.path = path

    @property
    def filepath(self):
        return os.path.expanduser(self.path)

    @property
    def config(self):
        try:
            with open(self.filepath, 'r') as config_buffer:
                return json.load(config_buffer)
        except FileNotFoundError:
            self.config = {}
            return {}
        except (json.JSONDecodeError,):
            return {}

    @config.setter
    def config(self, value):
        with open(self.filepath, 'w') as config_buffer:
            json.dump(value, config_buffer, indent=2)

    def update_configuration(self, key, **configuration):
        current_configuration = self.config
        if key not in current_configuration:
            current_configuration[key] = configuration
        else:
            current_configuration[key].update(configuration)
        self.config = current_configuration


class ReboticsScriptsConfiguration(DumpableConfiguration):
    def __init__(self, path, provider_class=RetailerProvider):
        super(ReboticsScriptsConfiguration, self).__init__(path)
        self.provider_class = provider_class

    def get_provider(self, key, api_verbosity=0):
        config = self.config.get(key, None)
        if config is None:
            return None

        provider_kwargs = {
            'host': config['host'],
            'role': key,
            'api_verbosity': api_verbosity,
        }
        if 'token' in config:
            provider_kwargs['token'] = config['token']

        provider = self.provider_class(**provider_kwargs)
        return provider

    def list_roles(self):
        return self.config.keys()


class ReboticsCLIContext(object):
    configuration_class = ReboticsScriptsConfiguration

    def __init__(self,
                 command,
                 role,
                 format,
                 verbose,
                 api_verbosity,
                 config_path,
                 provider_class,
                 click_context):
        self.command = command
        self.role = role
        self.format = format
        self.verbose = verbose
        self.api_verbosity = api_verbosity
        self.config_path = config_path
        self.provider_class = provider_class
        self.verbose_log(f"Config path: {self.config_path}")
        self.config_provider = self.configuration_class(self.config_path, self.provider_class)
        self.config = self.config_provider.config
        self.click_context = click_context

    @property
    def provider(self):
        provider = self.config_provider.get_provider(self.role, self.api_verbosity)

        if provider is None:
            raise click.ClickException(f'Role {self.role} is not configured.\n'
                                       f'Run: \n{self.command} -r {self.role} configure')
        return provider

    def update_configuration(self, **configuration):
        self.config_provider.update_configuration(self.role, **configuration)

    def format_result(self, items, max_column_length=30, keys_to_skip=None, force_format=None):
        force_format = force_format if force_format else self.format
        if force_format == 'json':
            click.echo(json.dumps(items, indent=2))
        elif force_format == 'id':
            click.echo(" ".join([str(item.get('id')) for item in items]))
        else:
            format_full_table(items, max_column_length=max_column_length, keys_to_skip=keys_to_skip)

    def verbose_log(self, message):
        if self.verbose:
            click.echo(message)

    def do_progress_bar(self) -> bool:
        return self.format not in ('id', 'json')


pass_rebotics_context = click.make_pass_decorator(ReboticsCLIContext, True)


class GroupWithOptionalArgument(click.Group):
    def parse_args(self, ctx, args):
        if args:
            if args[0] in self.commands:
                if len(args) == 1 or args[1] not in self.commands:
                    args.insert(0, '')
        super(GroupWithOptionalArgument, self).parse_args(ctx, args)


states = DumpableConfiguration(os.path.join(app_dir, 'command_state.json'))


def read_saved_role(command_name):
    roles = states.config.get('roles')
    if roles is None:
        return None
    role = roles.get(command_name)
    return role


def process_role(ctx, role, command_name):
    if not role:
        if ctx.invoked_subcommand != 'roles':
            raise click.ClickException(
                'You have not specified role to use. User `roles` sub command to see what roles are available'
            )
    else:
        states.update_configuration('roles', **{command_name: role})


def task_runner(ctx, task_func, ids, concurrency, **kwargs):
    task_arguments = []

    for id_ in ids:
        arguments = {
            'ctx': ctx,
            'id': id_,
        }
        arguments.update(kwargs)
        task_arguments.append(arguments)

    pool = Pool(concurrency)
    data_list = pool.map(task_func, task_arguments)

    format_processing_action_output(data_list, ctx.format)


def download_file_from_dict(d):
    ctx = d['ctx']
    if ctx.verbose:
        click.echo('>> Downloading file into %s' % d['filepath'], err=True)
    result = download_file(d['url'], d['filepath'])
    click.echo('<< Downloaded file into %s' % d['filepath'], err=True)
    return result


class UnrecognizedInputTypeByExtension(Exception):
    pass


def guess_input_type(ext):
    if ext.startswith('.'):
        ext = ext.strip('.')
    if ext in [
        'jpeg', 'jpg', 'png',
    ]:
        return 'image'
    elif ext in [
        'mp4', 'mov', 'avi'
    ]:
        return 'video'
    else:
        raise UnrecognizedInputTypeByExtension('File with extension %s is given' % ext)


def fetch_scans(ctx, processing_ids):
    processing_actions_list = []
    with ThreadPoolExecutor(max_workers=len(processing_ids)) as executor:
        futures = [executor.submit(ctx.provider.processing_action_detail, scan_id) for scan_id in processing_ids]
        for future in tqdm.tqdm(
            as_completed(futures),
            total=len(processing_ids),
            desc='Fetching scans',
            disable=not ctx.do_progress_bar(),
        ):
            processing_actions_list.append(future.result())
    return processing_actions_list


def downloads_with_threads(ctx, files, concurrency):
    with ThreadPoolExecutor(concurrency) as executor:
        futures = [
            executor.submit(remote_loaders.download, file[0], file[1])
            for file in files
        ]
        for _ in tqdm.tqdm(
            as_completed(futures), total=len(files), desc='Downloading files', disable=not ctx.do_progress_bar()
        ):
            pass


def refresh_urls_in_threads(ctx, file_urls):
    results = []
    refresh_url_func = ctx.provider.refresh_url

    with ThreadPoolExecutor(min(32, len(file_urls))) as executor:
        futures = [
            executor.submit(refresh_url_func, file_url)
            for file_url in file_urls
        ]
        for future in tqdm.tqdm(
            as_completed(futures),
            leave=False,
            total=len(file_urls),
            desc='Refreshing urls',
            disable=not ctx.do_progress_bar()
        ):
            results.append(future.result()['url'])
    return results


def run_with_processes(invoked, iterable, concurrency):
    with Pool(concurrency) as pool:
        for _ in tqdm.tqdm(
            pool.starmap(invoked, iterable)
        ):
            pass
        pool.close()
        pool.join()


def get_segmentation(segmentation_filepath):
    with open(segmentation_filepath, 'r') as fd:
        segmentation_file = json.load(fd)
    return segmentation_file['per_image']


def get_segmentation_mode(segmentation):
    mode = 'items'
    if segmentation[0].get('remote_url') is not None:
        mode = 'remote_url'
    return mode


def save_masks(ctx, root_folder, urls):
    path_to_save_masks = root_folder / 'all_masks'
    path_to_save_masks.mkdir(parents=True, exist_ok=True)

    list_with_downloaded_mask = [
        [url, path_to_save_masks / str(urlparse(unquote(url)).path).lstrip('/').split('/')[-1]]
        for url in urls
    ]

    downloads_with_threads(ctx, list_with_downloaded_mask, concurrency=len(list_with_downloaded_mask))
