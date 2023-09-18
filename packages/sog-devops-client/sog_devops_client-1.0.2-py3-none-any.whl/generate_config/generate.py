import requests
from tenacity import retry, stop_after_attempt, wait_fixed

# 定义重试请求次数
__retry_count = 5

# 定义调用生成配置文件接口函数
# stop_after_attempt：请求达到最大次数后停止
# reraise：请求停止后返回原始异常信息（默认返回的是重试请求的异常）
# wait_fixed：请求失败后5秒重试


@retry(stop=stop_after_attempt(max_attempt_number=__retry_count), wait=wait_fixed(5), reraise=True)
def __request_generate_config(fileName, filePath, user, env, token, requestUrl, request_data):
    # 构建其他参数
    request_data['apolloUser'] = user
    request_data['apolloEnv'] = env
    request_data['token'] = token

    # 调用接口
    response = requests.post(requestUrl, data=request_data, files={
                             'file': (fileName, open(filePath, 'rb'), 'application/octet-stream')})
    response.encoding = 'utf-8'
    if response.status_code == 200:
        # 下载文件
        with open(r"./%s" % fileName, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(response)

    return

# 定义调用同步配置中心接口函数
# stop_after_attempt：请求达到最大次数后停止
# reraise：请求停止后返回原始异常信息（默认返回的是重试请求的异常）
# wait_fixed：请求失败后5秒重试


@retry(stop=stop_after_attempt(max_attempt_number=__retry_count), wait=wait_fixed(5), reraise=True)
def __request_syn_apollo(user, env, publish, token, requestUrl, configTemplates, request_data):
    # 构建其他参数
    request_data['apolloUser'] = user
    request_data['apolloEnv'] = env
    request_data['isPublish'] = publish
    request_data['token'] = token

    # 构建文件参数
    request_files = []
    for index in range(len(configTemplates)):
        request_files.append(('files', (configTemplates[index][0], open(
            configTemplates[index][1], 'rb'), 'application/octet-stream')))
    # 调用接口
    response = requests.post(requestUrl,
                             data=request_data, files=request_files)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        print(response.text)
    else:
        raise Exception(response)
    return

# 生成配置


def generate_config(user, env, token, publish, synApollo,  generateConfigUrl, apolloUrl, configTemplates, request_data):
    host = ''
    if env == 'DEV':
        host = 'https://workflow-dev.sinoocean-test.com'
    elif env == 'FAT':
        host = 'https://workflow.sinoocean-test.com'
    elif env == 'UAT':
        host = 'https://workflow.sinoocean-uat.com'
    elif env == 'PRO':
        host = 'https://workflow.sinooceangroup.com'
    else:
        host = 'https://workflow-dev.sinoocean-test.com'

    # 如果未传接口地址则根据环境使用内部指定接口地址
    if generateConfigUrl == "":
        # 生成配置文件接口地址
        generateConfig_request_url = "%s/THRWebApi/DevOpsWebHooks/ApolloWebHooks/GenerateConfigByTemplate"
        generateConfigUrl = generateConfig_request_url % host
    if apolloUrl == "":
        # 根据模板编辑草稿到配置中心接口地址
        editDraft_request_url = "%s/THRWebApi/DevOpsWebHooks/ApolloWebHooks/EditDraft"
        apolloUrl = editDraft_request_url % host

    # 默认先执行生成本地文件接口
    for index in range(len(configTemplates)):
        __request_generate_config(
            configTemplates[index][0], configTemplates[index][1], user, env, token, generateConfigUrl, request_data)
    if synApollo:
        __request_syn_apollo(user, env, publish, token,
                           apolloUrl, configTemplates, request_data)
    return
