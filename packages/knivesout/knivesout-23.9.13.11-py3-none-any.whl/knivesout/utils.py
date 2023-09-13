from codefast.asyncio import asyncformer as aformer
import codefast as cf 

class ResetStdFiles(object):

    def __init__(self, file_size_limit: int = 100000) -> None:
        """Keep stdout size small, 100MB by default
        """
        self.file_size_limit = file_size_limit

    async def get_file_size(self, filepath: str) -> int:

        def filesize(filepath: str) -> int:
            return cf.shell('du -s {} | cut -f1'.format(filepath))

        return int(await aformer(filesize, filepath))

    async def rename_file(self, filepath):
        return await aformer(
            cf.shell, "mv {} {}".format(filepath, filepath + '.bak'))

    async def run(self):
        for f in ['/tmp/stdout.txt', '/tmp/stderr.txt']:
            filesize = await self.get_file_size(f)
            if filesize > self.file_size_limit:
                await self.rename_file(f)
