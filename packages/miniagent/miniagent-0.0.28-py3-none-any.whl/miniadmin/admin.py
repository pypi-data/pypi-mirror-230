import os
from github import Github, Repository, ContentFile
import requests
from argparse import ArgumentParser, Namespace

#copied from Nordgaren/Github-Folder-Downloade
class GitDownload:

    @staticmethod
    def _download(c: ContentFile, out: str):
        r = requests.get(c.download_url)
        output_path = f'{out}/{c.path}'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            print(f'downloading {c.path} to {out}')
            f.write(r.content)

    @staticmethod
    def download_folder(repo: Repository, folder: str, out: str, recursive: bool):
        contents = repo.get_contents(folder)
        for c in contents:
            if c.download_url is None:
                if recursive:
                    GitDownload.download_folder(repo, c.path, out, recursive)
                continue
            GitDownload._download(c, out)

    @staticmethod
    def download_file(repo: Repository, folder: str, out: str):
        c = repo.get_contents(folder)
        GitDownload._download(c, out)

    @staticmethod
    def get_args() -> Namespace:

        #repo_str = 'tanminkwan/local-agent'
        #path = 'test_project'

        parser = ArgumentParser()
        parser.add_argument('repo', help='The repo where the file or folder is stored')
        parser.add_argument('path', help='The folder or file you want to download')
        parser.add_argument('-o', '--out', default='.', required=False, help='Path to folder you want to download '
                                                                                    'to. Default is current folder + '
                                                                                    '\'downloads\'')
        parser.add_argument('-r', '--recursive', action='store_true', help='Recursively download directories. Folder '
                                                                        'downloads, only!')
        parser.add_argument('-f', '--file', action='store_true', help='Set flag to download a single file, instead of a '
                                                                    'folder.')
        return parser.parse_args()
    
def example_code_download():
    args = GitDownload.get_args()
    g = Github()
    repo = g.get_repo(args.repo)
    GitDownload.download_folder(repo, args.path, out='.', recursive=True)

if __name__ == '__main__':
    example_code_download()