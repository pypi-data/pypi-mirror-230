size_names = ("pagesize", "size", "limit")
page_names = ("pageNum", "current", "currentpage", "page")
before_names = ("before", "start")
end_names = ("end", )
page_and_size = size_names + page_names
before_and_end = before_names + end_names
before_and_end_re_str = "|".join(["^" + i for i in before_and_end] + [i + "$" for i in before_and_end])
