# -*- coding: UTF-8 -*-
from urllib.parse import urlparse, parse_qs


class CurlParser(object):
    def parse_url(self, url: str) -> dict:
        # 解析 URL
        parsed_url = urlparse(url)
        # 获取各个组成部分
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        path = parsed_url.path
        query = parsed_url.query
        query_params = parse_qs(parsed_url.query)
        return {
            "scheme": scheme,
            "netloc": netloc,
            "path": path,
            "query": query,
            "query_params": query_params,
        }

    # 处理curl中data部分的数据,把多行转换成一行数据
    def reduce_curl_data_part(self, lines, s, e):
        new_lines = []
        new_i = -1
        for i in range(s, e):
            new_line = lines[i]
            if "--data " in lines[i]:
                # 判断请求的body是否完整,根据''单引号是否是两个
                char_count = lines[i].count("'")
                if char_count == 1:
                    body_line = lines[i]
                    new_i = i
                    new_i += 1
                    while i < e:
                        body_line += lines[new_i]
                        if lines[new_i].count("'") == 1:
                            break
                        new_i += 1
                    new_lines.append(body_line)
            if i >= new_i:
                new_lines.append(new_line)
        return new_lines

    def get_curl_line_num_scope(self, lines):
        start_num = 0
        num = 0
        curl_num = 0
        line_num_array = []
        for line in lines:
            # 拆分多个curl
            if "curl" in line:
                curl_num += 1
                if curl_num >= 2:
                    line_num_array.append([start_num, num - 1])
                    curl_num = 1
                start_num = num
            num += 1
            if num == len(lines):
                line_num_array.append([start_num, num])
        return line_num_array

    def split_curl_to_struct(self, lines, s, e, curl_filter=None) -> dict:
        req_data = {}
        header = {}
        reduced_lines = self.reduce_curl_data_part(lines=lines, s=s, e=e)
        for i in range(0, len(reduced_lines)):
            lines_i_str = str(reduced_lines[i])
            line_i_list = lines_i_str.split(" ")
            if "curl" in lines_i_str:
                if curl_filter:
                    if curl_filter not in lines_i_str:
                        # 如果curl_filter 不存在于当前Url中,则跳过本次循环
                        continue
                for line_sub in line_i_list:
                    if line_sub.lower() in ["get", "put", "post", "delete"]:
                        req_data["method"] = line_sub.lower().replace("'", "")
                    elif "http" in line_sub:
                        req_data["original_url"] = line_sub.replace("'", "")
                    # 兼容Postman中url没有http开头的情况
                    elif "/" in line_sub:
                        req_data["original_url"] = line_sub.replace("'", "")
            elif "-X " in lines_i_str:
                line_i_list = lines_i_str.split(" '")
                req_data["method"] = (
                    line_i_list[1]
                    .lower()
                    .replace("'", "")
                    .replace(" ", "")
                    .replace("\\\n", "")
                )
            elif "-H '" in lines_i_str or "--header" in lines_i_str:
                line_i_list = lines_i_str.split(" '")
                subs = str(line_i_list[1]).split(":")
                if len(subs) > 1:
                    # TODO 空格区分有用和无用，目前cookie的value中会有包含空格的情况, 不删除
                    header[subs[0]] = (
                        subs[1].replace("'", "").replace("\\\n", "").replace(" ", "")
                    )
                else:
                    header[subs[0]] = ""
            elif "--data-raw" in lines_i_str or "--data" in lines_i_str:
                line_i_list = lines_i_str.replace(" $", " ").split(
                    " '"
                )  # TODO 有$符号,split会失败,这样解决会出现被错误替换的问题
                if len(line_i_list) > 1:
                    curl_data = line_i_list[1]
                else:
                    curl_data = line_i_list[0]
                req_data["body"] = (
                    curl_data.replace("'", "")
                    .replace(" ", "")
                    .replace("\\\n", "")
                    .replace("\n", "")
                )

                if not req_data.get("method"):
                    req_data["method"] = "post"

        req_data["header"] = header
        if not req_data.get("method"):
            req_data["method"] = "get"

        return req_data
