| Phase         | Agents  | Parallel?                     |
| ------------- | ------- | ----------------------------- |
| Foundation    | 00 → 01 | No                            |
| Core model    | 02      | No                            |
| Backend       | 03      | No                            |
| AI            | 04      | Can parallel with frontend    |
| Frontend      | 07      | Can parallel with AI          |
| Storage/media | 06      | Can parallel with AI/frontend |
| Pipeline      | 05      | After 02 + 04 + 06            |
| Integration   | 08      | No                            |
| QA            | 09      | No                            |
| Security      | 10      | No                            |
| Observability | 11      | Can overlap with QA           |
| Release       | 12      | Last                          |

