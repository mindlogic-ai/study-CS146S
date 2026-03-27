---
title: "/chat/completions"
description: "completions api 가이드"
order: 7
isFeatured: false
lastEditedDate: "2025-11-28"
---

# 오픈AI 메시지 생성

<OverviewCard>
  오픈AI API는 GPT 및 DALL·E 등 고성능 언어 및 이미지 생성 모델을 HTTP 기반 REST
  API로 제공합니다. 이 API를 통해 자연어 처리, 대화형 응답, 이미지 생성 등
  다양한 AI 기능을 통합할 수 있습니다.
</OverviewCard>

<Indent mt={12} />

- SDK: [오픈AI-python GitHub 링크](https://github.com/openai/openai-python)
- 공식 문서: [Chat API 문서 바로가기](https://platform.openai.com/docs/api-reference/chat)

| API                                                              | 지원 모델                                                                                                                                                                                                                                                                                                                                                                         |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [openai/chat/completions](/docs/factchat/api/openai-completions) | `gpt-5.1-chat-latest`<br />`gpt-5.1`<br />`gpt-5-chat-latest`<br />`gpt-5`<br />`gpt-5-mini`<br />`accounts/fireworks/models/gpt-oss-120b`<br />`grok-3-mini`<br />`grok-4`<br />`google/gemma-3-27b-it`<br />`accounts/fireworks/models/llama4-scout-instruct-basic`<br />`accounts/fireworks/models/llama4-maverick-instruct-basic`<br />`sonar-pro`<br />`sonar-reasoning-pro` |

---

### 오픈AI 챗 생성

<ParameterText badge="/v1/api/openai/chat/completions">POST</ParameterText>

오픈AI의 Chat API는 GPT 기반 모델을 사용하여 대화형 응답을 생성하는 엔드포인트입니다. 이 API를 사용하면 사용자의 메시지 히스토리를 바탕으로 AI가 적절한 응답을 생성해줍니다.

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
응답 생성을 위해 사용할 모델 ID입니다. 예: `gpt-5-chat-latest`

OpenAI는 다양한 기능, 성능 특성 및 가격대의 여러 모델을 제공합니다.

<ParameterText badge="array" required>
  messages
</ParameterText>
모델과의 대화 내역을 구성하는 메시지 배열입니다. 사용하는 모델에 따라 텍스트,
이미지, 오디오 등 다양한 메시지 유형(모달리티)을 지원합니다.

<ChildAttributes>

<ParameterText badge="object">Developer message</ParameterText>
모델이 반드시 따라야 할 지침을 포함한 메시지입니다. 최신 모델에서는 `system` 대신 사용됩니다.
<Indent>
<ParameterText badge="string | array" required>content</ParameterText>
지침 내용 (텍스트 또는 메시지 배열)

    <ParameterText badge="string" required>role</ParameterText>
    `"developer"`

    <ParameterText badge="string" optional>name</ParameterText>
    동일 역할 간 참여자 구분용 이름

  </Indent>

<ParameterText badge="object">User message</ParameterText>
사용자가 입력한 메시지입니다.
<Indent>
<ParameterText badge="string | array" required>content</ParameterText>
사용자 입력 내용

    <ParameterText badge="string" required>role</ParameterText>
    `"user"`

    <ParameterText badge="string" optional>name</ParameterText>

  </Indent>

<ParameterText badge="object">Assistant message</ParameterText>
모델이 생성한 응답 메시지입니다.
<Indent>
<ParameterText badge="string | array" required>content</ParameterText>
생성된 텍스트 응답

    <ParameterText badge="string" required>role</ParameterText>
    `"assistant"`

    <ParameterText badge="string" optional>name</ParameterText>

  </Indent>

<ParameterText badge="object">Tool message</ParameterText>
툴이 응답한 메시지입니다.
<Indent>
<ParameterText badge="string | array" required>content</ParameterText>
도구 실행 결과

    <ParameterText badge="string" required>role</ParameterText>
    `"tool"`

    <ParameterText badge="string" required>tool_call_id</ParameterText>
    어떤 호출에 대한 응답인지 식별하는 ID

  </Indent>

  </ChildAttributes>

<Indent mt={16} />

### example

```
curl https://factchat-cloud.mindlogic.ai/v1/api/openai/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $YOUR_API_KEY" \
  -d '{
    "model": "gpt-5.1-chat-latest",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'

```
