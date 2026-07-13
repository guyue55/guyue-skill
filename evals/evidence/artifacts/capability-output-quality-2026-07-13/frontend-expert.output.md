[Trace: Guyue/FrontendExpert] 识别产品类型、现有设计系统、技术栈与验证视口

## 实施方案

这是高频 B2B 后台表单，沿用现有 React 表单组件和 toast，不增加状态库、动画库或新的 UI 体系。

登录失败分为两类：

- **凭证失败**：在表单内持续显示统一错误：“登录失败，请检查账号和密码后重试。”未知账号、密码错误、账号停用等均不得在前端区分。
- **系统失败**：使用现有 toast 提示“暂时无法登录，请稍后重试。”不要展示接口原始错误、状态码或堆栈。

交互规则：

- 使用原生 `<form>` 和 `onSubmit`，支持 Enter 提交。
- 失败后将焦点移到表单错误摘要；用户继续输入时清除旧错误。
- 提交期间禁用按钮，防止重复请求；保留账号输入，不清空密码，避免增加键盘操作成本。
- 不用 toast 承载凭证错误：toast 会消失，不适合作为唯一错误反馈。
- 桌面端验证常见后台宽度；移动端至少验证 320px、375px、768px，无横向滚动。
- 后端必须统一未知账号与错误密码的响应结构，并实施限流。前端文案统一不能替代后端的防枚举控制。

## React 关键代码

以下 `FormInput`、`Button`、`toast` 和 `login` 替换为项目现有入口：

```tsx
import { FormEvent, useRef, useState } from 'react';
import { FormInput, Button } from '@/components';
import { toast } from '@/components/toast';
import { login } from '@/services/auth';

const CREDENTIAL_ERROR =
  '登录失败，请检查账号和密码后重试。';

type LoginValues = {
  account: string;
  password: string;
};

export function LoginForm() {
  const [values, setValues] = useState<LoginValues>({
    account: '',
    password: '',
  });
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const errorRef = useRef<HTMLDivElement>(null);

  function updateField(field: keyof LoginValues, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
    if (formError) setFormError('');
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;

    setFormError('');
    setSubmitting(true);

    try {
      await login(values);
      // 成功后的导航沿用现有认证流程。
    } catch (error: unknown) {
      if (isCredentialFailure(error)) {
        setFormError(CREDENTIAL_ERROR);

        requestAnimationFrame(() => {
          errorRef.current?.focus();
        });
      } else {
        toast.error('暂时无法登录，请稍后重试。');
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      className="loginForm"
      onSubmit={handleSubmit}
      aria-busy={submitting}
      noValidate
    >
      {formError && (
        <div
          ref={errorRef}
          id="login-error"
          className="loginError"
          role="alert"
          tabIndex={-1}
        >
          {formError}
        </div>
      )}

      <FormInput
        name="account"
        label="账号"
        autoComplete="username"
        value={values.account}
        disabled={submitting}
        aria-describedby={formError ? 'login-error' : undefined}
        onChange={(event) =>
          updateField('account', event.currentTarget.value)
        }
      />

      <FormInput
        name="password"
        type="password"
        label="密码"
        autoComplete="current-password"
        value={values.password}
        disabled={submitting}
        aria-describedby={formError ? 'login-error' : undefined}
        onChange={(event) =>
          updateField('password', event.currentTarget.value)
        }
      />

      <Button type="submit" disabled={submitting}>
        {submitting ? '正在登录…' : '登录'}
      </Button>
    </form>
  );
}
```

错误归类只消费稳定的接口错误类型，不匹配服务端原始文案：

```ts
type ApiError = {
  code?: string;
  status?: number;
};

function isCredentialFailure(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;

  const { code } = error as ApiError;

  // 服务端应将未知账号、密码错误、不可登录账号统一映射至此。
  return code === 'INVALID_CREDENTIALS';
}
```

不要编写这种映射：

```ts
// 错误：会泄露账号是否存在。
if (error.code === 'USER_NOT_FOUND') {
  setFormError('该账号不存在');
}
```

## 移动端与焦点样式

```css
.loginForm {
  display: grid;
  gap: 16px;
  width: min(100%, 400px);
  min-width: 0;
  margin-inline: auto;
}

.loginForm > * {
  min-width: 0;
}

.loginForm input,
.loginForm button {
  box-sizing: border-box;
  width: 100%;
  max-width: 100%;
}

.loginError {
  padding: 12px 16px;
  border: 1px solid hsl(0 55% 55%);
  border-radius: 6px;
  color: hsl(0 55% 32%);
  background: hsl(0 65% 97%);
  overflow-wrap: anywhere;
}

.loginError:focus-visible,
.loginForm :is(input, button):focus-visible {
  outline: 2px solid hsl(215 75% 45%);
  outline-offset: 2px;
}

@media (max-width: 480px) {
  .loginForm {
    width: 100%;
    gap: 12px;
  }

  .loginForm input {
    /* 避免部分移动浏览器因小字号自动放大页面。 */
    font-size: 16px;
  }
}
```

验收要点：

- Enter 可以提交，Tab 顺序为账号、密码、登录按钮。
- 失败摘要被读屏宣布并获得焦点，焦点轮廓清晰可见。
- 未知账号与错误密码显示完全相同的文案。
- 原始错误信息不会进入 DOM、toast 或日志。
- 重复点击只产生一次登录请求。
- 320px 宽度下没有横向滚动，长文案能够换行。
