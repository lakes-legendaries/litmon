"""Easy Azure interface"""

from argparse import ArgumentParser
from os import listdir, remove
from os.path import basename, dirname, isfile, join
import re

from azure.storage.blob import (
    BlobClient,
    BlobServiceClient,
    ContainerClient,
    ContentSettings,
)


class Azure:
    """Easy Azure Interface for uploading/downloading files

    This class requires that you have your account's Azure connection string
    saved in :code:`secrets_fname`. If you don't have this file, contact the
    administrator of this package.

    This class has a robust command-line interface. Run with the :code:`-h`
    flag for help.
    """

    public_container: str = 'litmon'
    """Azure public container"""

    private_container: str = 'litmon-private'
    """Azure private container"""

    resource_url: str = 'https://mfoundation.blob.core.windows.net'
    """Azure resource URL"""

    secrets_fname: str = 'secrets/azure'
    """Connection string file name"""

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
        regex: bool = False,
        replace: bool = False,
    ):
        """Download file from Azure

        Parameters
        ----------
        file: str
            file to download
        private: bool
            whether to download from private or public container
        regex: bool, optional, default=False
            treat :code:`file` as a regex expression. download all files that
            match. all files will be downloaded to the same directory.
        replace: bool, optional, default=False
            if :code:`dest/file` exists locally, then skip the download
        """

        # process regular expresion
        if regex:

            # download each file that matches pattern
            [
                cls.download(
                    file=join(dirname(file), _file),
                    private=private,
                    regex=False,
                    replace=replace,
                )
                for _file in cls._get_listing(file)
                if re.search(
                    basename(file),
                    join(dirname(file), _file)
                ) is not None
            ]

            # return to stop processing
            return

        # check if file exists
        if not replace and isfile(file):
            return

        # try to connect to Azure
        try:
            client: BlobClient = cls._connect().get_blob_client(
                container=(
                    cls.private_container
                    if private
                    else cls.public_container
                ),
                blob=basename(file),
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
        with open(file, 'wb') as f:
            f.write(client.download_blob().readall())

    @classmethod
    def upload(
        cls,
        /,
        file: str,
        *,
        private: bool,
        regex: bool = False,
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
        regex: bool, optional, default=False
            treat :code:`file` as a regex expression. upload all files that
            match. all files must be in the same directory.
        replace: bool, optional, default=True
            replace existing file on server if it exists
        update_listing: bool, optional, default=True
            if True, and :code:`not private`, then update directory listing
            (with :meth:`_update_listing`) after uploading
        """

        # process regular expresion
        if regex:

            # upload each file that matches pattern
            [
                cls.upload(
                    file=join(dirname(file), _file),
                    private=private,
                    regex=False,
                    replace=replace,
                    update_listing=False,
                )
                for _file in listdir(dirname(file))
                if re.search(file, join(dirname(file), _file)) is not None
            ]

            # update listing
            if update_listing and not private:
                cls._update_listing()

            # return to stop processing
            return

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

        # check if is html file
        if basename(file).rsplit('.')[-1] == 'html':
            content_settings = ContentSettings(content_type='text/html')
        else:
            content_settings = None

        # upload file
        with open(file, 'rb') as data:
            client.upload_blob(
                data,
                content_settings=content_settings,
            )

        # update directory listing
        if update_listing and not private:
            cls._update_listing()

    @classmethod
    def _get_listing(cls, private: bool) -> list[str]:
        """Get list of files on server

        Parameters
        ----------
        private: bool
            whether to query public or private container

        Returns
        -------
        list[str]
            list of files
        """

        # generate client
        client: ContainerClient = cls._connect().get_container_client(
            container=(
                cls.public_container
                if not private
                else cls.private_container
            ),
        )

        # get file list
        return [file['name'] for file in client.list_blobs()]

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

        # get file list
        files = cls._get_listing(private=False)

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
        cls.upload(
            fname,
            private=False,
            update_listing=False
        )

        # clean up
        remove(fname)


if __name__ == '__main__':

    # parse arguments
    parser = ArgumentParser('Upload to / download from Azure')
    parser.add_argument(
        'file',
        help='file name to upload/download',
    )
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
        '--regex',
        action='store_true',
        default=None,
        required=False,
        help='Treat file as a regular expression '
             '(upload/download all files that match)',
    )
    parser.add_argument(
        '--replace',
        type=bool,
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

    # set public / private
    args.private = True if args.private else False

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
