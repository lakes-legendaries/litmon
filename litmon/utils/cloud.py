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

    """Azure public container"""
    public_container: str = 'litmon'

    """Azure private container"""
    private_container: str = 'litmon-private'

    """Azure resource URL"""
    resource_url: str = 'https://mfoundation.blob.core.windows.net'

    """Connection string file name"""
    secrets_fname: str = 'secrets/azure'

    @classmethod
    def _connection_error(cls) -> str:
        """Connection exception error message

        Returns
        -------
        str
            error message
        """
        return re.sub(r'\s{2,}', ' ', f"""
            Couldn't find {cls.secrets_fname}, which is requied to access
            Azure resources. Contact the administrator of this package to
            obtain access.
        """)

    @classmethod
    def _connect(cls) -> BlobServiceClient:
        """Connect to Azure

        Returns
        -------
        BlobSericeClient
            Azure connection
        """

        # load connection string
        try:
            connection_str = open(cls.secrets_fname, 'r').read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(cls._connection_error())

        # return client
        return BlobServiceClient.from_connection_string(connection_str)

    @classmethod
    def download(
        cls,
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

        # check if file exists
        fname = file if dest is None else join(dest, file)
        if not replace and isfile(fname):
            return

        # try to connect to Azure
        try:
            client: BlobClient = cls._connect().get_blob_client(
                container=(
                    cls.private_container
                    if private
                    else cls.public_container
                ),
                blob=file,
            )

        # write error message
        except FileNotFoundError:
            if not replace:
                raise FileNotFoundError(re.sub(r'\s{2,}', ' ', f"""
                    File doesn't exist locally, and we couldn't connect to
                    Azure. Either obtain a local copy of {file} or place an
                    Azure connection string in {cls.secrets_fname}.
                """))
            else:
                raise FileNotFoundError(cls._connection_error())

        # download file
        with open(fname, 'wb') as f:
            f.write(client.download_blob().readall())

    @classmethod
    def upload(
        cls,
        /,
        file: str,
        *,
        private: bool,
        replace: bool = True,
        update_listing: bool = True,
    ):
        """Upload file to Azure

        Parameters
        ----------
        file: str
            file to upload. This file will be uploaded as
            :code:`basename(file)`. (I.e. it will NOT be uploaded to a
            directory within the container, but rather to the container root
            level.)
        private: bool
            whether to upload to private or public container
        replace: bool, optional, default=True
            replace existing file on server if it exists
        update_listing: bool, optional, default=True
            if True, and :code:`not private`, then update directory listing
            (with :meth:`_update_listing`) after uploading
        """

        # get client
        client: BlobClient = cls._connect().get_blob_client(
            container=(
                cls.private_container
                if private
                else cls.public_container
            ),
            blob=basename(file),
        )

        # delete existing
        if client.exists():
            if replace:
                client.delete_blob()
            else:
                return

        # upload file
        with open(file, 'rb') as data:
            client.upload_blob(data)

        # update directory listing
        if update_listing and not private:
            cls._update_listing()

    @classmethod
    def _update_listing(
        cls,
        /,
        *,
        fname: str = 'directory.html',
    ):
        """Update the directory listing for the public container

        This creates a simple, public html page that provides links to all
        files in the public container.

        Parameters
        ----------
        fname: str, optional, default='directory.html'
            temporary filename for directory listing
        """  # noqa

        # generate client
        client: ContainerClient = cls._connect().get_container_client(
            container=cls.public_container
        )

        # get file list
        files = [file['name'] for file in client.list_blobs()]

        # create html page
        container_url = f'{cls.resource_url}/{cls.public_container}'
        with open(fname, 'w') as fid:
            for file in files:
                if file == fname:
                    continue
                print(
                    f'<a href={container_url}/{file}>{file}</a><br>',
                    file=fid,
                )

        # upload directory listing
        cls.upload(fname, update_listing=False)

        # clean up
        remove(fname)


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
        required=False,
        help='to/from private container',
    )
    parser.add_argument(
        '--public',
        action='store_true',
        required=False,
        help='to/from public container',
    )
    parser.add_argument(
        '--dest',
        default=None,
        required=False,
        help='(Download only:) Download to this destination directory',
    )
    parser.add_argument(
        '--replace',
        action='store_true',
        default=None,
        required=False,
        help='Replace existing file (local for download / server for upload)',
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
    action(**kwargs)
