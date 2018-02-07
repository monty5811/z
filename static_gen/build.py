import os
import shutil
from hashlib import sha256

from jinja2 import Environment, FileSystemLoader

import mistune

from . import blog, render
from .constants import *
from .utils import load_yaml


def write_files(env, pages):
    manifest = {}
    for p in pages:
        # ignore headlines:
        if '_headlines' in p:
            continue
        data = load_yaml(p)
        content = data.copy()
        content.pop('layout', None)
        content.pop('title', None)
        result = env.get_template(data['layout'] + '.html').render(
            data=data,
            content=content,
            uri=p.replace(SRC_DIR, '').replace('.yml', ''),
        )

        new_path = p.replace(SRC_DIR, DIST_DIR)
        new_path = new_path.replace('.yml', '.html')
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        print(new_path)
        with open(new_path, 'w') as f:
            f.write(result)

        manifest[new_path.replace(DIST_DIR, '')] = sha256(result.encode()).hexdigest()[:8]

    return manifest


def write_sw(env, manifest):
    # add css and js:
    files = [
        '/static/css/stcs.css',
        '/static/js/stcs.js',
        '/headlines.html',
    ]

    for f_ in files:
        with open(DIST_DIR + f_, 'rb') as f:
            content = f.read()

        manifest[f_] = sha256(content).hexdigest()[:8]

    all_hashes = ''.join([k + v for k, v in manifest.items()])
    big_hash = sha256(all_hashes.encode()).hexdigest()[:8]

    result = env.get_template('sw.js').render({
        'manifest': manifest,
        'version': big_hash,
    })
    with open(os.path.join(DIST_DIR, 'sw.js'), 'w') as f:
        f.write(result)


def load_files(sub_dir=None):
    if sub_dir is not None:
        path = os.path.join(SRC_DIR, sub_dir)
    else:
        path = SRC_DIR
    for root, dirs, files in os.walk(path):
        for file_ in files:
            out = os.path.join(root, file_)
            yield out


def copy_static_files():
    dest = os.path.join(DIST_DIR, STATIC_DIR)
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(STATIC_DIR, dest)


def copy_public_files():
    dest = os.path.join(DIST_DIR)
    shutil.copytree(PUBLIC_DIR, dest)


def copy_src_files():
    dest = os.path.join(DIST_DIR, SRC_DIR)
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(SRC_DIR, dest)


def build():
    env = render.setup_jinja()
    shutil.rmtree(DIST_DIR, ignore_errors=True)
    copy_public_files()
    copy_static_files()
    blog.write_blog_index(env, load_files(sub_dir='_headlines'))
    manifest = write_files(env, load_files())
    write_sw(env, manifest)
