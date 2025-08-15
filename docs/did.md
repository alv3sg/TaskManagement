Domain (clean, framework‑free)

Value Objects

Email: normalizes (trim + lowercase) and validates format; raises InvalidEmail.

UserId: wraps a uuid.UUID with UserId.new() factory.

PasswordHash: opaque wrapper; rejects obviously invalid hashes.

Entities

User: fields id: UserId, email: Email, password_hash: PasswordHash, status: UserStatus, created_at.

Behaviors: change_email, change_password, ensure_can_authenticate (raises UserLocked), lock, issue_refresh_token(...).

RefreshToken: fields id: UUID, user_id: UserId, issued_at, expires_at, revoked_at.

Behaviors: ensure_active() (raises TokenExpired if expired/revoked), revoke().

Errors (domain)

DomainError base; specialized: UserLocked, TokenExpired, InvalidEmail.

Invariants

Usuário bloqueado não autentica.

E‑mail sempre normalizado e válido no momento da criação.

Refresh token só é válido se não estiver expirado nem revogado.

Application (use cases + ports/contracts)

Ports (interfaces/Protocol)

UserRepository: add, save, get_by_id, get_by_email, exists_by_email, list.

PasswordHasher: hash, verify.

(Preparado para incluir) RefreshTokenRepository, AccessTokenEncoder nos casos de login/refresh.

Use Cases (CRUD de usuário)

CreateUser: cria User com UserId.new(), valida Email, gera PasswordHash via PasswordHasher, impede e‑mail duplicado.

GetUser, ListUsers: leitura por id e paginação básica.

UpdateUserEmail: troca e‑mail com validação e prevenção de duplicidade.

UpdateUserPassword: redefine a senha aplicando novo PasswordHash.

SetUserStatus: lock/unlock do usuário.

DeleteUser: soft‑delete via lock (seguro para auditoria).

Teste facilitado

Repositório fake em memória e hasher fake permitem TDD sem banco ou framework.

Decisões-chave que estamos seguindo

DDD + Clean Architecture: módulos por contexto (bounded contexts), dependências apontando para dentro (interfaces → aplicação → domínio; infraestrutura → aplicação).

Domínio sem frameworks: nada de Pydantic/ORM/JWT no core.

Access token ≠ domínio: JWT/Paseto é transporte; ficará em AccessTokenEncoder (aplicação/infra).
Refresh token = domínio: modelado como entidade com ciclo de vida.

O que falta para fechar Auth end‑to‑end

Infraestrutura (quando terminar seu estudo de Mongo):

MongoUserRepository, MongoRefreshTokenRepository.

Argon2PasswordHasher (ou Bcrypt).

(Depois) JWTAccessTokens (AccessTokenEncoder).

Use cases de sessão:

Login: verifica senha, emite RefreshToken, gera access token (curto).

RefreshSession: valida/rotaciona refresh, gera novo access token.

Logout: revoga refresh token (ou todos do usuário).

Interfaces (HTTP):

Rotas FastAPI chamando os use cases e convertendo DTOs ↔ VO/Entidades.