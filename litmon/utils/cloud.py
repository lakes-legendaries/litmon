"""Easy Azure interface"""

from argparse import ArgumentParser
from os import remove
from os.path import basename, isfile, join
import re

from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient


class Azure:
    """Easy Azure Interface for uploading/downloading files

    This class requires that you have your account's Azure connection string
    saved in :code:`secrets_fname`. If you don't have this file, contact the
    administrator of this package.

    Parameters
    ----------
    public_container: str, optional, default='litmon'
        public container for sharing results
    private_container: str, optional, default='litmon-private'
        private container for internal data files
    secrets_fname: str, optional, default='secrets/azure'
        file containing your Azure connection string

    Attributes
    ----------
    client: BlobServiceClient
        client for interfacing with Azure
    """
    def __init__(
        self,
        /,
        private_container: str = 'litmon-private',
        public_container: str = 'litmon',
        secrets_fname: str = 'secrets/azure',
    ):
        # save passed
        self._public_container = public_container
        self._private_container = private_container

        # load connection string
        try:
            connection_str = open(secrets_fname, 'r').read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(re.sub(r'\s{2,}', ' ', f"""
                Couldn't find {secrets_fname}, which is requied to access Azure
                resources. Contact the administrator of this package to obtain
                access.
            """))

        # activate client
        self.client = BlobServiceClient.from_connection_string(connection_str)

    def _get_container(self, /, private: bool) -> str:
        """Get container name

        Parameters
        ----------
        private: bool
            whether you want the private or public container name

        Returns
        -------
        str
            name of requested container
        """
        return (
            self._public_container
            if not private
            else self._private_container
        )

    def download(
        self,
        /,
        file: str,
        *,
        private: bool,
        dest: str = None,
        replace: bool = False,
    ):
        """Download file from Azure

        Parameters
        ----------
        file: str
            file to download
        private: bool
            whether to download from private or public container
        dest: str, optional, default=None
            destination directory
        replace: bool, optional, default=False
            if :code:`dest/file` exists locally, then skip the download
        """
        bclient: BlobClient = self.client.get_blob_client(
            container=self._get_container(private),
            blob=file,
        )
        fname = file if dest is None else join(dest, file)
        if replace or not isfile(fname):
            with open(fname, 'wb') as f:
                f.write(bclient.download_blob().readall())

    def upload(
        self,
        /,
        file: str,
        *,
        private: bool,
        update_listing: bool = True,
    ):
        """Upload file to Azure

        Parameters
        ----------
        file: str
            file to upload
        private: bool, optional, default=False
            whether to upload to private or public container
        update_listing: bool, optional, default=True
            if True, and :code:`not private`, then update directory listing
            (with :meth:`_update_listing`) after uploading
        """

        # get client
        bclient: BlobClient = self.client.get_blob_client(
            container=self._get_container(private),
            blob=basename(file),
        )

        # upload file
        with open(file, 'rb') as data:
            bclient.upload_blob(data, private=False)

        # update directory listing
        if update_listing and not private:
            self._update_listing()

    def _update_listing(
        self,
        /,
        *,
        temp_fname: str = 'directory.html',
        url: str = 'https://mfoundation.blob.core.windows.net',
    ):
        """Update the directory listing for the public container

        This creates a simple, public html page that provides links to all
        files in the public container.

        Parameters
        ----------
        temp_fname: str, optional, default='directory.html'
            temporary filename for directory listing
        url: str, optional, default='https://mfoundation.blob.core.windows.net'
            storage account url
        """  # noqa

        # generate client
        cclient: ContainerClient = self.client.get_container_client(
            container=self._public_container
        )

        # get file list
        files = [file['name'] for file in cclient.list_blobs()]

        # create html page
        full_url = f'{url}/{self._public_container}'
        with open(temp_fname, 'w') as fid:
            for file in files:
                if file == temp_fname:
                    continue
                print(
                    f'<a href={full_url}/{file}>{file}</a><br>',
                    file=fid,
                )

        # upload directory listing
        self.upload(temp_fname, update_listing=False)

        # clean up
        remove(temp_fname)


if __name__ == '__main__':

    # parse arguments
    parser = ArgumentParser('Upload to / download from Azure')
    parser.add_argument(
        '-u',
        '--upload',
        action='store_true',
        required=False,
        help='upload file',
    )
    parser.add_argument(
        '-d',
        '--download',
        action='store_true',
        required=False,
        help='download file',
    )
    parser.add_argument(
        '-f',
        '--file',
        required=True,
        help='file name',
    )
    parser.add_argument(
        '--private',
        action='store_true',
        help='to/from private container',
    )
    parser.add_argument(
        '--public',
        action='store_true',
        help='to/from public container',
    )
    parser.add_argument(
        '--dest',
        help='(Download only:) Download to this destination directory',
    )
    parser.add_argument(
        '--replace',
        action='store_true',
        help='(Download only:) If file exists locally, then skip download',
    )
    args = parser.parse_args()

    # check args
    if args.upload == args.download:
        raise ValueError('You must choose to either upload or download')
    if args.public == args.private:
        raise ValueError('You must choose the public or private container')

    # get action
    action = Azure.upload if args.upload else Azure.download

    # get kwargs
    kwargs = {
        key: value for key, value in vars(args).items()
        if value is not None
        and key != 'public'
        and key != 'upload'
        and key != 'download'
    }

    # run action
    action(Azure(), **kwargs)
