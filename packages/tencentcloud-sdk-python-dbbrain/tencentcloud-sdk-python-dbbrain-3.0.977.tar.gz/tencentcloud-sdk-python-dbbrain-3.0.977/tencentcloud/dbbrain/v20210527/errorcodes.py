# -*- coding: utf8 -*-
# Copyright (c) 2017-2021 THL A29 Limited, a Tencent company. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# CAM签名/鉴权错误。
AUTHFAILURE = 'AuthFailure'

# DryRun 操作，代表请求将会是成功的，只是多传了 DryRun 参数。
DRYRUNOPERATION = 'DryRunOperation'

# 操作失败。
FAILEDOPERATION = 'FailedOperation'

# 内部错误。
INTERNALERROR = 'InternalError'

# 参数错误。
INVALIDPARAMETER = 'InvalidParameter'

# 参数取值错误。
INVALIDPARAMETERVALUE = 'InvalidParameterValue'

# 超过配额限制。
LIMITEXCEEDED = 'LimitExceeded'

# 缺少参数错误。
MISSINGPARAMETER = 'MissingParameter'

# 操作被拒绝。
OPERATIONDENIED = 'OperationDenied'

# CAM鉴权错误。
OPERATIONDENIED_USERHASNOSTRATEGY = 'OperationDenied.UserHasNoStrategy'

# 请求的次数超过了频率限制。
REQUESTLIMITEXCEEDED = 'RequestLimitExceeded'

# 资源被占用。
RESOURCEINUSE = 'ResourceInUse'

# 资源不足。
RESOURCEINSUFFICIENT = 'ResourceInsufficient'

# 资源不存在。
RESOURCENOTFOUND = 'ResourceNotFound'

# 资源不可用。
RESOURCEUNAVAILABLE = 'ResourceUnavailable'

# 资源售罄。
RESOURCESSOLDOUT = 'ResourcesSoldOut'

# 未授权操作。
UNAUTHORIZEDOPERATION = 'UnauthorizedOperation'

# 未知参数错误。
UNKNOWNPARAMETER = 'UnknownParameter'

# 操作不支持。
UNSUPPORTEDOPERATION = 'UnsupportedOperation'

# 该时间范围内的审计日志已下载
UNSUPPORTEDOPERATION_HASDUPLICATEDTASK = 'UnsupportedOperation.HasDuplicatedTask'
