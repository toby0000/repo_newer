# repo_newer
获取某仓库的fork开发者的更新的提交。

由于某些仓库可能由于拥有者放弃维护，导致无法合并一些fork开发者有用的commit。
所以该脚本可以获取相对于指定仓库更新的提交，以便及时合并有用的commit


# 用法
`python main.py <user:passwd> <repo_name> [since]`

如: `python main.py user:passwd toby0000/redis-simple-cache 2016-10-10T00:00:00Z`
则获取toby0000/redis-simple-cache源项目vivekn/redis-simple-cache的所有forks项目，
在2016-10-10T00:00:00Z时间后的所有commit.
如果没有提供since参数：
则该时间默认为toby0000/redis-simple-cache项目最后一个commit提交的时间+1秒
