# Task 4: Improve Tests for Pagination and Sorting

## Goal
Notes와 Action Items의 페이지네이션/정렬 테스트 커버리지 강화. 프로덕션 코드 변경 없음.

## Test Cases

### Notes
- limit 적용, skip+limit 조합, skip이 전체 데이터 초과 시 빈 리스트
- sort by title asc/desc, sort by created_at asc/desc
- invalid sort field → fallback to -created_at
- search(q) + pagination 조합

### Action Items
- limit 적용, skip+limit 조합, skip 초과 시 빈 리스트
- sort by description asc/desc, sort by created_at asc/desc
- completed filter + pagination 조합
- invalid sort field → fallback
