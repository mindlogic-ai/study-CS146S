---
title: "/messages"
description: "앤트로픽 메시지 API 가이드"
order: 2
isFeatured: false
lastEditedDate: "2025-11-28"
---

# 앤트로픽 메시지 생성

<OverviewCard>
  앤트로픽의 Message API는 Claude 모델을 기반으로 작동하며, 사용자와의 대화
  흐름을 이해하고 이에 맞는 응답을 생성합니다. 대화 내용은 messages 필드에
  입력하며, 요청 시 다양한 설정을 통해 스트리밍 또는 비스트리밍 방식의 응답을
  받을 수 있습니다. 이미지 블록 삽입, 외부 도구 사용, 시스템 프롬프트 지정 등
  고급 기능도 함께 제공합니다.
</OverviewCard>

<Indent mt={12} />

- SDK: [앤트로픽 SDK](https://docs.Anthropic.com/ko/api/client-sdks)
- 공식 문서: [앤트로픽 공식 문서](https://docs.Anthropic.com/en/api/messages)

| API                                                         | 지원 모델                                                                                     |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| [anthropic/messages](/docs/factchat/api/anthropic-messages) | `claude-sonnet-4-5-20250929`<br />`claude-opus-4-5-20251101`<br />`claude-haiku-4-5-20251001` |

---

### 메시지 생성

<ParameterText badge="/v1/api/anthropic/messages">POST</ParameterText>

Claude 모델은 입력된 메시지 배열을 기반으로 자연스러운 대화 응답을 생성합니다.
시스템 프롬프트, 도구 호출, 이미지 입력, 스트리밍 출력 등을 조합해 활용할 수 있습니다.

---

### 요청 헤더

```json
Authorization: Bearer {api-key}
```

---

### 파라미터

<ParameterText badge="string" required>
  model
</ParameterText>
응답 생성을 위해 사용할 모델 ID입니다. Claude 3 이상의 모델을 사용하는 것이
권장되며, 더 넓은 기능 범위를 제공합니다. 예시: `claude-sonnet-4-5-20250929`

<ParameterText badge="array" required>
  messages
</ParameterText>
모델에 전달할 대화 메시지 배열입니다. base64로 인코딩된 이미지를 포함할 수
있습니다. 전체 구조는 [Messages](https://docs.Anthropic.com/en/api/messages)를
참고하세요.

<Banner variant="info">
  `messages`는 `user`와 `assistant` 역할이 번갈아 구성된 배열이어야 하며,
  `system` 역할은 별도의 `system` 필드로 설정해야 합니다.
</Banner>

<Banner variant="warning">
  이미지 입력 시에는 base64 인코딩과 함께 `media_type`을 반드시 지정해야 합니다.
  지원되는 포맷은 `jpeg`, `png`, `gif`, `webp`입니다.
</Banner>

<ParameterText badge="integer" required>
  max_tokens
</ParameterText>
생성할 최대 토큰 수입니다. 모델은 이 값을 초과하지 않도록 응답을 종료합니다.
상한은 [모델
리스트](https://docs.Anthropic.com/en/docs/about-claude/models/all-models)마다
다릅니다.

<ParameterText badge="string">system</ParameterText>
모델의 역할 또는 동작을 정의하는 시스템 프롬프트입니다.

<ParameterText badge="boolean">stream</ParameterText>
스트리밍 응답을 받을지 여부입니다. 기본값: `false`

<Banner>
  `stream`이 활성화되면 응답은 Server-Sent Events 방식으로 실시간 전달되며, 토큰
  단위로 수신됩니다. `thinking`, `tool_choice`, `tools`와 같은 기능은 Claude 3
  이상에서 지원됩니다.
</Banner>

<Indent mt={16} />

### example

```
curl https://factchat-cloud.mindlogic.ai/v1/api/anthropic/messages \
  -H "Authorization: Bearer $YOUR_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-4-5-20251101",
    "max_tokens": 1024,
    "messages": [
      { "role": "user", "content": "Say this is a test!" }
    ]
  }'
```
