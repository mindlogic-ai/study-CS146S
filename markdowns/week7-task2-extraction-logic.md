# Task 2: Extend Extraction Logic

## Goal
Action item 추출을 구조화된 데이터로 반환하고, 패턴 인식 확장

## Changes
- ExtractedItem dataclass (text, priority, deadline, category)
- 추가 키워드: FIXME, BUG, HACK, TASK, FOLLOW-UP, REMINDER
- Priority 감지: urgent/critical/asap → high, nice to have/eventually → low
- Deadline 추출: by/due/before/deadline 패턴
- Category 감지: bug, review, feature, task
- POST /notes/{id}/extract 엔드포인트
