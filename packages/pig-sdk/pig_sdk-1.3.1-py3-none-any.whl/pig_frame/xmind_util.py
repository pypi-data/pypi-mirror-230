# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2
# @File : xmind_util.py
"""
文件说明：支持通过数据对象生成xind文件，支持将测试用执行结果生成xind文件，做业务沉淀
"""
import os
from pig_frame import log
import xmind


class XmindUtil:
    def create_xmind_file(self, data, path="", file_name="xmind"):
        try:
            path = path + "/" + file_name + ".xmind"
            if os.path.exists(path):
                os.remove(path)
            w = xmind.load(path)
            s = w.getPrimarySheet()
            s.setTitle(file_name)
            for k in data.keys():
                r = s.getRootTopic()
                r.setTitle(k)
                self.add_sub_topic(r, data.get(k))
            xmind.save(w, str(path))
        except Exception as e:
            log.error(str(e))

    def add_sub_topic(self, root, data):
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for k in item.keys():
                        if k == "comment":
                            # root.addComment(item.get(k))
                            pass
                        else:
                            r = root.addSubTopic()
                            if item.get("comment") is not None:
                                r.addComment(item.get("comment"))
                            r.setTitle(k)
                            self.add_sub_topic(r, item.get(k))
                elif isinstance(item, list):
                    self.add_sub_topic(root, item)
                else:
                    r = root.addSubTopic()
                    r.setTitle(item)

        else:
            r = root.addSubTopic()
            r.setTitle(data)


if __name__ == "__main__":
    data = {
        "测试用例": [
            {
                "场景": [
                    {"case01": "mock"},
                    {"case01": "mock"},
                    {"case01": "mock"},
                    {"case01": "mock"},
                    {"case01": "mock"},
                ]
            }
        ]
    }

    XmindUtil().create_xmind_file(data)
