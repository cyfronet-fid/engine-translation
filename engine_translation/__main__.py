import json
import sys

import click
import os
import yaml


@click.command()
@click.argument('yaml_dir', type=click.Path(file_okay=False, resolve_path=True))
@click.argument('output', type=click.File(mode='w', encoding='utf-8', atomic=True), default='-')
def main(yaml_dir, output):
    """

    :param yaml_dir:
    :type yaml_dir: str
    :param output:
    :type output: file
    :rtype: None
    """

    tl = []

    def default_ctor(loader, tag_suffix, node):
        if tag_suffix == 'java.util.ArrayList':
            return loader.construct_sequence(node, deep=True)
        else:
            return loader.construct_mapping(node, deep=True)

    yaml.add_multi_constructor('!', default_ctor)

    def find_labels(d):
        if 'label' in d:
            yield d['label']

        if 'body' in d:
            yield d['body']

        if 'description' in d:
            yield d['description']

        for k in d:
            if isinstance(d, str):
                continue
            if isinstance(d[k], list):
                for i in d[k]:
                    for j in find_labels(i):
                        yield j

    for root, dir, files in os.walk(yaml_dir):
        for fpath in filter(lambda x: x.endswith('.yml'), files):
            with open(os.path.join(root, fpath)) as f:
                tl += list(find_labels(yaml.load(f)))

    try:
        with open(output.name) as existing_f:
            tl_dict = json.loads(existing_f.read())
    except (ValueError, IOError):
        tl_dict = {}

    for s in tl:
        if s not in tl_dict:
            tl_dict[s] = ""

    output.write(unicode(json.dumps(tl_dict, indent=4, sort_keys=True)))


if __name__ == '__main__':
    main()
