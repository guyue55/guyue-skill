[Trace: Guyue/DebuggingMindset] 建立症状、假设与最低充分证据边界

## 当前判断

故障已高置信度定位在 **Nginx 或其前置代理的请求体限制层**，不是应用代码：

- Nginx access log 记录 `413 Payload Too Large`。
- 应用日志完全没有收到请求，说明请求大概率在进入应用前被拒绝。
- 小于 1MB 正常、8MB 必现，具有明显的请求体大小边界。
- “偶发”很可能是只有大文件触发；如果同样大小也偶发，则要检查多个 Nginx 实例配置是否不一致。

但目前还不能断言一定是 `client_max_body_size`，缺少 Nginx error log、`upstream_status` 和生效配置。

## 最低充分验证

先锁定一条失败请求的时间、路径、Host 和 request ID，然后检查：

```bash
rg 'client intended to send too large body| 413 ' /var/log/nginx/error.log /var/log/nginx/access.log
```

若 error log 出现类似 `client intended to send too large body`，即可证明是当前 Nginx 在读取请求体时拒绝。

检查 access log 中以下字段：

- `status=413`
- `upstream_status=-`：当前 Nginx 本地拒绝，请求未转发。
- `upstream_status=413`：413 来自后面的代理或网关，继续沿代理链排查。
- `request_length`：确认失败与请求体大小相关。

读取实际生效配置，而非只看源码中的配置文件：

```bash
nginx -T 2>&1 | rg -n -C 4 'server_name|location|client_max_body_size|proxy_pass'
```

`nginx -T` 可能输出证书路径或其他敏感配置，分享结果前需脱敏。

如果运行在 Kubernetes Ingress，还需只读检查：

```bash
kubectl get ingress -A -o yaml | rg -n -C 4 'proxy-body-size|client-max-body-size|nginx'
kubectl get pods -A -l app.kubernetes.io/name=ingress-nginx -o wide
```

并分别检查每个 Ingress Controller 实例的生效配置，排除副本配置漂移。

## RCA 矩阵

| 假设 | 当前证据 | 最小验证 | 判定信号 |
|---|---|---|---|
| 当前 Nginx 请求体上限不足 | 高度吻合 | error log + `nginx -T` | `too large body`，且 `upstream_status=-` |
| 多个 Nginx 实例配置不一致 | 可解释同尺寸偶发 | 按实例关联失败请求并比较配置 | 同一请求大小在不同实例结果不同 |
| 413 来自后置网关 | 尚未排除 | 查看 `upstream_status` | `upstream_status=413` |
| 应用主动返回 413 | 证据不支持 | 关联应用访问日志和 trace ID | 应用确实收到请求才成立 |

## 受控复现

在测试环境或安全测试账号中，对同一路径、同一认证、同一文件类型测试 1、2、4、6、8MB，记录 HTTP 状态、实际请求长度和命中的 Nginx 实例。Multipart 上传存在额外封装开销，不能只按文件大小判断请求体大小。

如果 4MB 成功而更大的请求在固定边界失败，并伴随 Nginx `too large body`，根因即可闭环。

## 止血与修复边界

- 不要重试：413 是确定性拒绝，重试只会增加流量。
- 暂时在客户端明确提示当前上传上限，避免用户反复提交。
- 如果发布同时修改过网关配置，可在确认差异后恢复已知正常配置。
- 根因确认后，应统一所有代理层和实例的上传限制；上限应覆盖产品允许的最大文件及 multipart 开销。
- 不建议未经验证直接调大限制。还需同步评估超时、临时文件、磁盘、内存和安全边界；大文件场景优先考虑已有的对象存储直传能力。

**当前状态：高置信度定位到代理请求体限制，精确根因仍等待 Nginx error log、`upstream_status` 和生效配置确认。**
