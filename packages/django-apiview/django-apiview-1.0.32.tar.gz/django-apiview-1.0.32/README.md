# django-apiview

## 安装

```
pip install django-apiview
```

## 关于其它依赖包的说明

- `django-apiview`中的`@cache`功能依赖于`django-redis`包。但我们并未将`django-redis`当成我们的依赖包，因为很多应用可能不会使用`@cache`功能。如果你需要使用`@cache`功能，则你需要将`django-redis`作为你的项目的依赖包。
- `django_apiview.clients.ApiviewClient`使用到了`requests`包，同理，我们也没有将其当成我们的依赖包。如果你需要使用`django_apiview.clients.ApiviewClient`，你也需要将`requests`作为你的项目的依赖包。

## 使用

```
from django_apiview.views import apiview

@apiview
def ping():
    """总是返回"pong"字符串常量。

    --------
    @methods: get
    @response: 200 OK "正确的响应" {{{
        "pong"
    }}}
    @response: 200 ERROR "错误的响应" {{{
        {
            "code": 1234,
            "message": "错误原因。"
        }
    }}}
    """
    return "pong"


@apiview
@string_length_limit("msg", max_length=4096, min_length=2)
def echo(msg: str):
    """总是返回你输入的内容。

    要求参数msg的长度范围为：[2, 4096]。

    --------
    @methods: post
    @parameter: body {{{
        in: body
        required: true
        example:
          msg: "测试的字符串"
    }}}
    @response: 200 OK "正确的响应" {{{
        "测试的字符串"
    }}}
    @response: 500 ERROR "错误的响应" {{{
        {
            "code": 1234,
            "message": "错误原因。"
        }
    }}}
    """
    return msg
```

1. 使用django-apiview定义接口，总是要加上@apiview注解，并且要求是第一个注解。
1. 可以使用多个辅助注解来进行参数检查和其他各类检查。
1. 接口函数只要返回业务层数据即可，django-apiview会对其进行序列化和业务协议封装。
1. 支持swagger接口管理界面自动生成。所有需要在swagger接口管理界面中显示的接口，需要在其docstring中添加swagger配置。

## 辅助注解

- django_apiview.helpers.auth
    - check_aclkey: 检查请求头/请求参数/请求数据中是否有aclkey字段，并且aclkey字段是否有效。
- django_apiview.helpers.cache
    - cache: 接口缓存支持。支持模型数据变动联动缓存清理。
- django_apiview.helpers.cipher
    - rsa_decrypt: 密码字段rsa加解密。
    - decode_encrypted_data: 业务数据整体rsa加解密。
- django_apiview.helpers.request_methods（如果不添加任何请求方式控制，则根据全局设置允许全部）
    - allow_get: 允许get请求方式。
    - allow_post: 允许post请求方式。
    - allow_put: 允许put请求方式。
    - allow_delete: 允许delete请求方式。
    - allow_patch: 允许patch请求方式。
    - allow_head: 允许head请求方式。
    - allow_options: 允许options请求方式。
- django_apiview.helpers.transformer
    - body_alias: 将body整体赋给新的变量
    - cookie_variable: 将cookie值赋给新的变量
    - meta_variable: 将meta值赋给新的变量
- django_apiview.helpers.validators
    - requires: 设置必填参数。
    - choices: 设置参数选项范围。
    - between: 设置参数取值范围。
    - string_length_limit: 设置参数长度范围。

## Swagger集成

### Swagger集成效果图

![django_apiview swagger集成效果](https://github.com/zencore-dobetter/pypi-images/raw/main/django-apiview/swagger.png)

### Swagger集成

*pro/settings.py*
```
INSTALLED_APPS = [
    ...
    "django_static_swagger_ui",
    "django_apiview",
    ...
]
```

*pro/urls.py*

```
from django.urls import path
from django.urls import include

urlpatterns = [
    ...
    path('apiview/', include("django_apiview.urls")),
    ...
]
```

- 配置如上。访问：http://127.0.0.1:8000/apiview/swagger-ui.html。
- 如何控制swagger的输出范围以及如何配置接口的swagger输出详见下面说明。

### Swagger Docstring规则

#### parameter规则

```
@parameter: <parameter_name> {{{
    <parameter_attributes>
}}}
```

- parameter_name: 字符串，变量名。
- parameter_attributes: json或yaml格式。遵循swagger-ui的参数语法。部分参数字段如下：
    - `in: [body, path, query, formData]` 表示参数来源
    - `required: true/false` 表示字段是否必填
    - `example:` 表示参数示例
    - `schema:`
        - `$ref: #/components/schemas/ModelName` 表示参数模型
    - `type: integer/string` 表示参数类型
- `@parameter:`，可以多次使用，显示多个参数。各参数的in属性可以不同，表示参数可以有不同的来源。
- `in: body`，较为特殊，一般只有一个，表示以json payload形式提交的数据整体。

使用举例：

```
@parameter: body {{{
    in: body
    required: true
    example:
        msg: "Example Message"
}}}
```

- `in: body`，表示参数使用json payload形式提交。
- `required: true`，表示参数是必填的。
- `example:\n    msg: "Example Message"`，表示参数示例，将显示在swagger的参数输入框中。

#### response规则

```
@response: <http_status_code> <respones_status> <respones_description> {{{
    <response_body>
}}}
```

- `http_status_code`，表示http响应状态码。一般为200，404，500等。除非系统级错误，正确响应和一般业务逻辑错误推荐使用200。
- `respones_status`，取值为OK或ERROR，表示业务状态。OK表示业务处理正确。ERROR表示业务处理异常。
- `respones_description`，表示本响应示例的业务说明。
- `response_body`，表示示例的响应体。只需要显示有效的业务数据部分即可。django-apiview或自动进行业务数据的封装，最终显示为完整的响应数据包。
- `@response`，可以多次使用，可以用来表示在不同情况下的响应。

使用举例：

```
@response: 200 OK "正确的响应" {{{
    "测试的字符串"
}}}
```

- `200`，表示http状态码为正确的http响应。
- `OK`，表示业务逻辑处理正确完成。
- `正确的响应`，表示以下的响应未例为正常情况下的响应数据。
- `测试的字符串`，表示返回的有效业务数据内容。如果使用SimpleJsonResultPacker业务封装协议，则最终显示的响应案例数据为：
    ```
    {
        "success": true,
        "result": "测试的字符串"
    }
    ```

#### Swagger数据模型

在每个app的__init__.py文件中，可以使用以下配置项输出该应用下的数据模型。

- `DJANGO_APIVIEW_SWAGGER_EXPORT_ALL_MODELS = True`，表示是否将该应用下的所有数据库模型输出为swagger-ui数据模型。True表示输出所有数据模型。False表示不输出所有模型。默认为False，表示不输出。
- `DJANGO_APIVIEW_SWAGGER_EXPORT_MODELS = []`，表示输出列表中指定的数据模型。数据模型可以为Django的数据库模型，也可以是Django的表单。使用类引用路径，如：`django_apiview_example.forms.EchoForm`。


#### Swagger其它说明

1. 接口的简述是docstring的第一行。
1. 接口的详细描述是docstring中分割符以上的所有字符串。
1. docstring分割符是指8个以的连续-号字符串。建议将@methods/@parameter/@response等定义放在分割符以后。

## 业务数据封装协议

django-apiview提供自带了多种可供使用的业务数据封装协议。默认为SimpleJsonResultPacker。

### SimpleJsonResultPacker

正确的响应:

```
{
    "success": true,
    "result": <any>
}
```

- success=true，表示业务逻辑处理正确完成。
- result，表示业务逻辑正确完成的情况下返回的有效数据。

错误的响应：

```
{
    "success": false,
    "error": {
        "code": <error_code>
        "message": <error_message>
    }
}
```

- success=false，表示业务逻辑处理异常。
- error，表示具体的错误信息。
    - error.code表示错误码。
    - error.message表示错误原因。
- 一个设计良好的系统，不同原因的错误应该使用不同的错误码，且一个错误码总是对应相同的错误原因。
- 错误原因应该有模板化支持，在保持错误原因整体信息不变的情况下，可以适当填充不同的字段名等。

### SafeJsonResultPacker

在SimpleJsonResultPacker的基础上，进行数据加密。

{
    "encryptedPassword": "xxx",
    "encryptedData": "xxx",
}

- `encryptedPassword`，在随机生成的本次加密密码的RSA加密结果。
- `encryptedData`，在SimpleJsonResultPacker业务数据封装序列化结果，使用本次加密密码进行aes加密的结果。
- 系统在生成加密数据时，必须知道数据接收端的RSA公钥。
- 系统接收端必须能获取到自己的RSA私钥。

### DeetrResultPacker

```
{
    "data": <any>,
    "errcode": 0,
    "errmsg": "OK",
    "time": "2022-09-10 23:09:33",
    "reqid": "67aa6f147d074c2c8bed121c1994f80d",
}
```

- data，表示有效的业务数据。任意可json序列化的数据。如果业务逻辑处理异常，则将data置None或空字符串。特殊场景下，也允许逻辑错误时，使用data字段返回错误相关数据。但错误信息一般不在本字段返回。
- errcode，表示业务逻辑错误码。0表示业务逻辑处理正常，非0表示业务逻辑异常。
- errmsg，表示业务逻辑处理错误信息。如果业务逻辑处理正常则建议返回常量OK。
- time，接口数据的生成时间。推荐使用用户可读的字符串格式，方便用户调试之用。
- reqid，请求的流水号。推荐在nginx中生成。

### DmrsPacker

```
{
    "data": <any>,
    "message": "OK or <error message>",
    "returnCode": 0,
    "successSign": True,
}
```

- data，表示有效的业务数据。任意可json序列化的数据。如果业务逻辑处理异常，则将data置None或空字符串。特殊场景下，也允许逻辑错误时，使用data字段返回错误相关数据。但错误信息一般不在本字段返回。
- message，表示业务逻辑处理错误信息。如果业务逻辑处理正常则建议返回常量OK。
- returnCode，表示业务逻辑错误码。0表示业务逻辑处理正常，非0表示业务逻辑异常。
- successSign，表示业务逻辑处理是否成功。True表示成功，则data字段为有效业务数据，同时一般returnCode为0，message一般为OK或正常。False表示异常，此时returnCode一般为非0表示错误码，message表示错误信息，同时data一般为空。

## 配置项

以下为可配置在`pro/settings.py`中的配置项。

### Swagger相关配置项

- `DJANGO_APIVIEW_SWAGGER_UI_TITLE = "You App Title"`
- `DJANGO_APIVIEW_SWAGGER_UI_DESCRIPTION = "Your App description"`
- `DJANGO_APIVIEW_SWAGGER_UI_VERSION = "Your APP version"`
- `DJANGO_APIVIEW_SWAGGER_UI_TERMS_OF_SERVICE = "Your App Terms of Service URL"`
- `DJANGO_APIVIEW_SWAGGER_UI_CONTACT_EMAIL = "Your email address"`
- `DJANGO_APIVIEW_SWAGGER_UI_API_HOST = "Your site url"`
- `DJANGO_APIVIEW_SWAGGER_FIELDS = {"SchemaField": ("BaseClass", {"extra_key": "extra_value"})}`
    - `SchemaField`，是在数据模型定义中使用的字段或在数据表单定义中使用的字段。一般是应用使用了自定义的字段才需要在此注册。
    - `BaseClass`，是`django_apiview.swagger_ui.field.SchemaField`子类的全路径。如果你的`SchemaField`指向的类是一个数据模型字段，推荐使用`django_apiview.swagger_ui.field.ModelField`，如果你的类是一个表单字段，推荐使用`django_apiview.swagger_ui.field.FormField`。
    - `extra_key` and `extra_value`，是你额外指定的最终应用到swagger模型字段的属性。一般要求有：type。其它属性根据type而定。具体查看swagger-ui的模型定义规则。

### 接口总体控制

- `DJANGO_APIVIEW_DEFAULT_ALLOW_METHODS = ["get", "post"]`，接口请求方式的允许范围。如果接口没有单独的请求方式控制，则接口允许接收这里所列的所有请求方式。接口可以单独设置允许的请求方式，以突破这里的限制。
- `DJANGO_APIVIEW_PACKER = "django_apiview.pack.SimpleJsonResultPacker"`，业务数据封装协议。默认为：django_apiview.pack.SimpleJsonResultPacker。

### 辅助函数关联控制

#### django_apiview.helpers.auth.check_aclkey关联配置

- `DJANGO_APIVIEW_ACLKEY = ""`，允许的aclkey值。
- `DJANGO_APIVIEW_ACLKEYS = []`，允许的aclkey值列表。两者可以同时生效。一般如果允许设置多个ACLKEY则使用DJANGO_APIVIEW_ACLKEYS，只允许一个ACLKEY则使用DJANGO_APIVIEW_ACLKEYDJANGO_APIVIEW_ACLKEY。


## 版本历史

### v1.0.32

- Swagger认证机制。
- 修正路径参数的问题。

### v1.0.19

- 内部重构。对外API保持兼容的情况下有所增强。
- 提供更多种类的业务数据封装协议。
- 提供更多的辅助装饰器。
- 集成Swagger UI。


### v0.9.29及以下

- 提供apiview基本功能。
