import os
import glob
from google.cloud import storage
from liveramp_automation.utils.log import Logger


class BucketHelper:
    def __init__(self, project_id, bucket_name):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(self, local_file_path, cloud_blob_path):
        """Upload a local file or files under the folder to the cloud storage bucket.

        :param local_file_path: Local file path for uploading.
        :param cloud_blob_path: Destination blob path within the bucket.
        :return: Size of the uploaded file in bytes.
        """
        Logger.info("Start upload_file")
        Logger.info(f"File = {local_file_path} on Path = {cloud_blob_path}")
        if os.path.isfile(local_file_path):
            blob = self.bucket.blob(os.path.join(cloud_blob_path, os.path.basename(local_file_path)))
            result = blob.upload_from_filename(local_file_path)
            Logger.info(f"Item Uploded on Path = {local_file_path}")
        for item in glob.glob(local_file_path + '/*'):
            if os.path.isfile(item):
                Logger.info(f"Found Item =  {os.path.basename(item)} on Path = {local_file_path}")
                if item == ".keep":
                    continue
                blob = self.bucket.blob(os.path.join(cloud_blob_path, os.path.basename(item)))
                result = blob.upload_from_filename(item)
                Logger.info(f"Uploaded Item =  {os.path.basename(item)} on Path = {local_file_path}")
        if result is None:
            result = 0
        return result

    def check_file_exists(self, file_path):
        """Check if a file exists in the bucket.

        :param file_path: Path to the bucket file.
        :return: Boolean.
        """

        Logger.info("Start check_file_exists")
        Logger.info(f"Path = {file_path}")
        blob = self.bucket.blob(file_path)
        result = blob.exists()
        Logger.info(f"Result = {result}")
        Logger.info("Finish check_file_exists")
        return result

    def download_file(self, source_blob_name, destination_file_path):
        """Download a file from the bucket.

        :param source_blob_name: Path to the bucket file.
        :param destination_file_path: Path to the download file.
        :return: None."""

        Logger.info("Start download_file")
        Logger.info(f"File = {source_blob_name} download on Path = {destination_file_path}")
        try:
            blobs = self.bucket.list_blobs(prefix=source_blob_name)
            for blob in blobs:
                if blob.name.endswith("/"):
                    continue
                file_name = os.path.join(destination_file_path, os.path.basename(blob.name))
                blob.download_to_filename(file_name)
                Logger.info("Finish download_file")


            # blob = self.bucket.blob(source_blob_name)
            # blob.download_to_filename(destination_file_path)
            # Logger.info("Finish download_file")
            return 1
        except Exception as e:
            Logger.error(e)
            return 0

    def list_files_with_substring(self, substring):
        """Gets a list of files that contain a substring in the name.

        :param substring: string to find on the file name.
        :return: array with the match list."""

        Logger.info("Start list_files_with_substring")
        Logger.info(f"Substring = {substring}")
        blobs = self.bucket.list_blobs()
        matching_files = []

        for blob in blobs:
            if substring in blob.name:
                Logger.info(f"Found Matching File = {blob.name}")
                matching_files.append(blob.name)

        Logger.info(f"Result = {matching_files}")
        Logger.info("Finish list_files_with_substring")
        return matching_files

    def get_total_rows(self, file_path):
        """Gets the total number of rows in a file.

        :param file_path: path of the file.
        :return: integer with the total row."""

        Logger.info("Start get_total_rows")
        Logger.info(f"Path = {file_path}")
        blob = self.bucket.blob(file_path)
        content = blob.download_as_text()
        total_rows = len(content.split('\n'))
        Logger.info(f"Result = {total_rows}")
        Logger.info("Finish get_total_rows")
        return total_rows

    def read_file_content(self, file_path):
        """Gets the entire content of a file.

        :param file_path: path of the file.
        :return: string content of the file."""

        Logger.info("Start read_file_content")
        Logger.info(f"Path = {file_path}")
        blob = self.bucket.blob(file_path)
        content = blob.download_as_text()
        Logger.info(f"Result = {content}")
        Logger.info("Finish read_file_content")
        return content

    def read_file_lines(self, file_path, num_lines):
        """Gets the first n lines of a file.

        :param file_path: path of the file.
        :param num_lines: number of fist lines.
        :return: string content of the file."""

        Logger.info("Start read_file_lines")
        Logger.info(f"First {num_lines} of the Path = {file_path}")
        blob = self.bucket.blob(file_path)
        content = blob.download_as_text()
        lines = content.split('\n')
        selected_lines = lines[:num_lines]
        result = '\n'.join(selected_lines)
        Logger.info(f"Result = {result}")
        Logger.info("Finish read_file_content")
        return result
