from promptmanager.runtime.flow import PMRuntime
import logging


class TextTruncation:
    def __int__(self):
        pass
    def exec(self,max_length,text:str):
        split_len = max_length if max_length > len(text) else len(text)
        text[0:split_len:]

def run(runtime:PMRuntime)->dict:
    logger = logging.getLogger('root')
    logger.info("This is runtime info:")
    max_length = runtime.params.script.max_length
    logger.info(runtime.show_info())
    text_truncation = TextTruncation()
    result = text_truncation.exec(max_length,runtime.inputs.text)
    result_obj ={ "output" : result }