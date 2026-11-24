# Phase 4 — DevOps & AWS

**Dates:** 2027-08-09 → 2027-10-17 (W37–W46) · **Buffer:** W47, 2027-10-18 → 2027-10-24
**Prerequisites:** Phase 1 (OS, networking), Phase 3 (Dockerized API) · [← Phase 3](03-backend.md) · [Learning path](../learning-path.md) · [Next: Phase 5 →](05-data-engineering.md)

## Goal

Take QuizLab from "runs on my laptop" to "runs on AWS, deployed automatically, monitored, and torn down or rebuilt with one command." Data platforms are infrastructure. Phase 5 (data engineering) and Phase 7 (AI) both build on the cloud foundation, CI/CD and Terraform skills from this phase.

> **Cost rule:** set a **budget alarm before creating anything**. Use the smallest instance sizes, avoid NAT gateways (they cost ~$30+/month; use public subnets for Fargate tasks or VPC endpoints instead), and `terraform destroy` when not actively working. Check the current AWS Free Tier terms when opening the account.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | Linux admin: users, permissions, processes, systemd, logs, networking tools | [The Linux Command Line](https://linuxcommand.org/tlcl.php) (selected chapters) | Cheat sheet: `chmod`, `ps`, `ss`, `journalctl`, `top` |
| 2 | Docker deep-dive: layers, caching, multi-stage, networks, volumes, image security | [Docker docs: build best practices](https://docs.docker.com/build/building/best-practices/) | Explain how a container differs from a VM (link to Phase 1 OS notes) |
| 3 | CI/CD concepts; GitHub Actions workflows, jobs, services, caching, secrets | [GitHub Actions docs](https://docs.github.com/en/actions) | My CI pipeline design (stages + gates) |
| 4 | Cloud fundamentals; AWS global infrastructure; IAM (users, roles, policies) | [AWS Skill Builder](https://skillbuilder.aws/): Cloud Practitioner Essentials (free) | Explain role vs user vs policy with an example |
| 5 | AWS networking: VPC, subnets, route tables, security groups, ALB | Skill Builder + [VPC user guide](https://docs.aws.amazon.com/vpc/latest/userguide/) basics | Draw the QuizLab VPC |
| 6 | Infrastructure as Code: Terraform state, modules, plan/apply, remote state | [Terraform AWS tutorials](https://developer.hashicorp.com/terraform/tutorials/aws-get-started) | Why IaC beats clicking in the console |
| 7 | Containers on AWS: ECR, ECS Fargate, task definitions; RDS; Secrets Manager | [Getting started with ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started.html) + RDS docs | ECS concepts map (cluster, service, task) |
| 8 | Deployment strategies (rolling, blue/green), rollbacks; the 12-factor app | [12factor.net](https://12factor.net/) | Which factors QuizLab already follows |
| 9 | Monitoring & SRE: SLIs/SLOs, alerting, on-call basics | [Google SRE book](https://sre.google/sre-book/table-of-contents/) ch. 4 & 6 | 2 SLOs for QuizLab |
| 10 | Security & cost: least privilege, OIDC for CI, secrets; cost management | [AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html): security + cost pillars | Threat list + cost plan |

## Project track (in `quizlab`)

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | 12-factor config with `pydantic-settings`; `Makefile` (or `justfile`) for dev tasks (`make test`, `make up`, `make migrate`) | One-command dev workflow | Linux, config |
| 2 | Harden the Dockerfile: non-root user, slim base, `.dockerignore`, healthcheck; scan with [Trivy](https://trivy.dev/); record image size before/after | Smaller, safer image | Docker |
| 3 | GitHub Actions **CI**: ruff → mypy → pytest (Postgres service container) → start compose → `postman collection run` (Postman CLI) | Green CI badge | CI |
| 4 | AWS account: root MFA, IAM Identity Center user, **budget alarm**, AWS CLI profile; S3 upload via CLI and `boto3` | `docs/aws-setup.md` | IAM, AWS CLI |
| 5 | Terraform: remote state (S3), VPC with public/private subnets, security groups | `infra/terraform/network/` | IaC, networking |
| 6 | Terraform: ECR, RDS Postgres (private subnet), Secrets Manager, Redis | `infra/terraform/data-stores/` | IaC, managed services |
| 7 | Terraform: ECS Fargate services (api, worker), ALB; Alembic migrations as a one-off ECS task | Public URL serving `/docs` | Containers on AWS |
| 8 | **CD**: GitHub OIDC → AWS role (no long-lived keys); build → push to ECR → deploy on merge to `main` → Postman CLI smoke test against the live URL; written rollback steps | `.github/workflows/deploy.yml` | CD |
| 9 | CloudWatch: log groups, dashboard (requests, errors, p95 latency, DB CPU), alarms → SNS email | Dashboard screenshot in README | Monitoring |
| 10 | IAM least-privilege review; `terraform destroy` → `apply` drill (time it); cost doc; runbook; tag `v0.4.0` | `docs/runbook.md`, `docs/cost.md` | Security, ops |

## Done when

- [ ] I can explain the QuizLab network path, from the internet through the ALB and ECS to RDS.
- [ ] Merging to `main` deploys automatically and runs Postman smoke tests.
- [ ] No long-lived AWS keys exist anywhere (OIDC only).
- [ ] I can destroy and rebuild the whole stack in < 30 minutes.
- [ ] Budget alarm works; monthly cost is documented.

## Threads this phase

- **Statistics / DSA / SQL:** 1 each per week.
- **Writing:** ADR 0006 (ECS Fargate vs EC2 vs Kubernetes), ADR 0007 (Terraform module layout).
- **Optional cert:** AWS Certified Cloud Practitioner. If I take it, plan ~2 extra weeks.

## Stretch goals

- Run QuizLab on local Kubernetes ([kind](https://kind.sigs.k8s.io/) or k3d) with Helm, to learn K8s concepts without paying for EKS.
- OpenTelemetry traces exported to AWS X-Ray.
- Staging environment with Terraform workspaces.
