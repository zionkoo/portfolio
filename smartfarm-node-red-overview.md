# Smart Farm Node-RED 공개 플로우 안내

이 문서는 Smart Farm 교육 프로젝트의 Node-RED 운영 백업을 분석해 공개 가능한 범위만 정리한 설명 자료입니다.

## 공개 범위

- `smartfarm-node-red-public.json`은 실제 프로젝트의 Node-RED 플로우를 기반으로 민감정보를 제거한 공개용 참고 자료입니다. 별도의 환경 설정 없이 즉시 실행되는 구성은 아닙니다.
- 원본의 Telegram Bot Token, Chat ID, MQTT 인증값, 브로커 주소, 내부 IP, 장치 경로, 세션 및 관리자 설정은 포함하지 않습니다.
- 공개 파일은 인증값과 환경별 연결 정보를 직접 입력해야 하므로 운영 백업처럼 즉시 실행되지 않습니다.
- 원본 ZIP과 운영 환경 설정은 수정하지 않았으며 공개 저장소에 포함하지 않습니다.

## 실제 탭과 역할

### 1. Smartfarm

- Arduino Serial In에서 줄 단위 JSON 수신
- JSON 노드에서 문자열을 객체로 변환
- `function 1`에서 `temp`와 `humidity`를 분리
- MQTT `farm/temp`, `farm/humidity` 토픽으로 각각 발행
- `Save Temp Humidity`에서 최신 온도·습도와 측정 시각을 Node-RED 전역 컨텍스트에 저장
- MQTT `farm/pump`의 `ON`·`OFF`를 `PUMP_ON`·`PUMP_OFF` 시리얼 명령으로 변환

```text
DHT11 -> Arduino -> Serial In -> JSON -> function 1
                                         |-> MQTT Out: farm/temp ------> Dashboard
                                         |-> MQTT Out: farm/humidity --> Dashboard
                                         `-> Save Temp Humidity
                                              `-> Global latest values

Inject (3,600s) -> read Global latest values -> Telegram Sender
```

대시보드 전달과 Telegram 전달은 하나의 직렬 흐름이 아닙니다. `function 1`에서 온습도 토픽 발행과 최신값 저장으로 나뉘고, Telegram 메시지는 별도의 3,600초 Inject가 저장값을 읽어 생성합니다.

### 2. SmartFarm Hourly History

- MQTT `farm/#`를 구독해 최신 온도·습도를 플로우 컨텍스트에 저장
- 3,600초마다 해당 값을 시간 단위 스냅샷으로 생성
- `farm/history/YYYY-MM-DD/HH` 토픽에 retained 메시지로 발행
- 별도 데이터베이스 노드는 확인되지 않아 장기 DB 보존 완료로 보지 않습니다.

### 3. Telegram Bot

- 3,600초 주기 Inject 노드 실행
- 전역 컨텍스트의 최신 온도·습도와 측정 시각 참조
- 메시지 본문 구성 후 Telegram Sender로 전달
- 실제 프로젝트에서 1시간 간격 메시지 수신을 확인했습니다.

## 검증 범위

| 구분 | 확인 내용 | 상태 |
|---|---|---|
| DHT11 | 실제 온도·습도 측정 및 대시보드 표시 | 실물 검증 완료 |
| LED | 대시보드 ON/OFF에 따른 실제 점등·소등 | 실물 검증 완료 |
| Telegram | 1시간 간격 온습도 메시지 수신 | 수신 검증 완료 |
| 시간별 기록 | retained MQTT 스냅샷 생성 코드 | 코드 확인 |
| 펌프 | 명령 변환 및 자동 OFF 로직 | 실제 펌프 미검증 |
| EC·pH | 실물 센서 미사용 | 미검증 |

## 재현 전 필요한 설정

1. MQTT 브로커 주소와 TLS·인증 설정
2. Arduino 시리얼 장치 경로
3. Telegram Bot 설정과 수신 대상 식별자
4. `node-red-node-serialport`, `node-red-contrib-telegrambot` 설치

민감정보는 Node-RED Credential Store 또는 환경 변수로 관리하고 공개 JSON에 직접 기록하지 않는 것을 권장합니다.
