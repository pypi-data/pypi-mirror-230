import base64
import os

from yantu.api_requestor import _make_request


class YantuObject:
    def __init__(self, yantu_key=None):
        self.yantu_key = yantu_key

    def upload_doc(self, doc_path):
        """
        私域知识库文档上传
        :param doc_path: 文档路径
        :return:
        """
        data = {
            'yantu_key': self.yantu_key,
            'doc': base64.b64encode(open(doc_path, 'rb').read()).decode('utf-8'),
            'doc_name': os.path.basename(doc_path)
        }
        response = _make_request('uploadDoc', data)
        open(doc_path, 'rb').close()  # 关闭文件
        return response.text

    def get_doc_list(self):
        """
        获取私域知识库文档列表
        :return:
        """
        data = {
            'yantu_key': self.yantu_key
        }
        response = _make_request('getDocList', data)
        json_res = response.json()
        if 'doc_list' in json_res:
            return json_res['doc_list']
        else:
            return json_res['res']

    def delete_doc(self, filename):
        """
        删除私域知识库中文档
        :param filename: 文档名称
        :return:
        """
        data = {
            'yantu_key': self.yantu_key,
            'filename': filename
        }
        response = _make_request('deleteDoc', data)
        return response.text

    def doc_qa(self, question):
        """
        基于私域知识库中内容进行文档问答
        :param question:
        :return:
        """
        data = {
            'yantu_key': self.yantu_key,
            'question': question
        }
        response = _make_request('docQA', data)
        answer = response.text
        return answer