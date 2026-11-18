# ✦ Manager AI PRO ✦

> **Trilingual CLI Manager (PT-BR / EN / ZH-CN) for Google AI Pro (5TB) Trial Activation & Subscription Proration Stacking (up to 30 Months)**  
> **Gerenciador CLI Trilíngue para Ativação e Acumulação do Google AI Pro (5TB) por até 30 Meses**  
> **Google AI Pro (5TB) 免费试用激活与订阅升级叠加三语 CLI 管理器（最高累计 30 个月）**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Frida 16.5.9](https://img.shields.io/badge/Frida-16.5.9-orange.svg)](https://frida.re/)
[![Android 12](https://img.shields.io/badge/Android-12%20(Root)-brightgreen.svg)](#)

---

## 🌐 Idiomas / Languages / 语言导航

- 🇧🇷 [**Português (PT-BR)**](#-documentação-em-português-pt-br)
- 🇺🇸 [**English (EN)**](#-english-documentation-en)
- 🇨🇳 [**简体中文 (ZH-CN)**](#-中文文档-zh-cn)

---

# 🇧🇷 Documentação em Português (PT-BR)

## 📖 Visão Geral e Transparência 100% Open Source

O **Manager AI PRO** é uma interface de linha de comando (CLI) interativa, moderna e 100% transparente que unifica todas as etapas de verificação de ambiente, injeção do `BillingClient` via Frida e acumulação (stacking) de ofertas gratuitas do plano **Google AI Pro (5 TB)** diretamente pelo aplicativo oficial **Google One** em um emulador Android 12 com Root.

### Como funciona por baixo dos panos? (Sem segredos)

A Google Play Store possui ofertas promocionais de teste gratuito para o SKU `g1.2tb.ai.subs_variant` (**Google AI Pro 5TB**) que não aparecem na interface web comum, mas são retornadas pela API nativa `BillingClient.queryProductDetailsAsync` dentro do Android:

1. **Ofertas disponíveis no SKU `g1.2tb.ai.subs_variant`:**
   - `12months-eft` → **12 meses gratuitos** (Passo 1)
   - `6months-eft` → **+6 meses gratuitos** (Passo 2 · acumula para 18 meses)
   - `6months-eft-2` → **+6 meses gratuitos** (Passo 3 · acumula para 24 meses)
   - `6months-eft-ss-2026` → **+6 meses gratuitos** (Reserva · acumula até 30 meses)

2. **Por que os meses se somam em vez de substituir?**
   - Se você apenas iniciar uma nova compra, a Play Store substitui a assinatura atual mantendo a mesma data.
   - O **Manager AI PRO** lê o `purchaseToken` da sua assinatura ativa diretamente do banco SQLite local da Play Store (`/data/data/com.android.vending/databases/library.db`) e invoca o fluxo oficial de **Upgrade de Assinatura** (`BillingFlowParams.SubscriptionUpdateParams`) com:
     ```java
     SubscriptionUpdateParams.newBuilder()
         .setOldPurchaseToken(oldPurchaseToken)
         .setReplaceProrationMode(5) // 5 = CHARGE_FULL_PRICE
         .build();
     ```
   - No modo `CHARGE_FULL_PRICE (5)`, o sistema de faturamento da Google Play converte e adia integralmente o período gratuito restante, somando os novos 6 meses ao final do seu ciclo atual com cobrança imediata de **$0,00**.

3. **Segurança e Privacidade:**
   - Todo o código roda **100% localmente** entre o seu computador e o seu emulador Android via ADB.
   - Nenhuma senha, token ou dado de cartão é enviado para servidores externos.

---

## 🛠️ Pré-requisitos Obrigatórios

1. **Emulador Exclusivo — MuMuPlayer ([https://www.mumuplayer.com/pt/](https://www.mumuplayer.com/pt/)) no ANDROID 12:**
   - O **[MuMuPlayer](https://www.mumuplayer.com/pt/)** é o **ÚNICO emulador suportado** pelo projeto.
   - O MuMuPlayer **PRECISA estar rodando o Android 12**.
   - ⚠️ *Caso o seu MuMuPlayer esteja no Android 15 (ou outra versão), desinstale a imagem atual e instale a imagem do **Android 12**.*
2. **Permissão ROOT Ativada:**
   - Ative o **Modo Root** nas configurações do MuMuPlayer e mantenha a **Depuração ADB** habilitada.
3. **Conta Google e Aplicativos:**
   - Faça login na sua conta Gmail desejada na **Google Play Store** (a conta precisa ter um método de pagamento/cartão vinculado e **não** pode ter nenhuma assinatura ativa do Google One antes de começar).
   - Baixe o aplicativo oficial **Google One** na Play Store.
   - Após instalar, **reinicie a emulação no MuMuPlayer** e deixe a **Google Play Store** e o **Google One** abertos.

---

## 🚀 Como Usar o Manager AI PRO

Basta dar dois cliques em **`Manager AI PRO.bat`** (no Windows) ou executar via terminal:

```bash
python manager_ai_pro.py
```

Logo ao abrir, escolha o idioma (**Português PT-BR**, **English** ou **简体中文**). Você verá o menu interativo:

| Opção no Menu | Função Detalhada | Regra de Desbloqueio / Segurança |
| :--- | :--- | :--- |
| **1. Instalar ambiente** | Verifica Python (3.10+), instala `frida==16.5.9`, encontra ou baixa o `adb` (Platform-Tools) e conecta ao MuMuPlayer. | Sempre disponível. Fica **VERDE** no menu após concluído! |
| **2. Preparar ambiente** | Exibe um alerta destacado sobre **MuMuPlayer + Root + Android 12 + Login na Play Store + App Google One aberto** (exige confirmação `[✓ ENTENDI]` pelo teclado) e roda o autodiagnóstico completo. | Sempre disponível. Desbloqueia a Opção 3 após passar com sucesso. |
| **3. Ativar 12 Meses PRO** | Injeta a oferta `12months-eft` (`pro12`) no emulador e abre a folha de confirmação da Play Store. | Só roda se o **Passo 2** tiver passado com sucesso. Exige aceitar a oferta na tela do emulador. |
| **4. (1) Ativar +6 Meses PRO** | Lê o `purchaseToken` atual e injeta o upgrade `6months-eft` (`pro6`) somando +6 meses (Total: 18 meses). | Só roda se o **Passo 3** tiver sido concluído e aceito no emulador. |
| **5. (2) Ativar +6 Meses PRO** | Lê o `purchaseToken` atual e injeta o upgrade `6months-eft-2` (`pro6b`) somando +6 meses (Total: 24 meses). | Só roda se o **Passo 4** tiver sido concluído e aceito no emulador. |
| **6. Reserva +6 Meses** | Injeta o pacote reserva `6months-eft-ss-2026` (`pro6c`) caso alguma opção anterior não tenha funcionado ou para somar +6 meses extras. | Disponível com aviso obrigatório de aceitação na tela do emulador. |
| **7. Ajuda** | Exibe o manual completo de instruções e solução de problemas traduzido no idioma selecionado. | Sempre disponível. |
| **8. Sair** | Encerra o gerenciador com segurança. | Sempre disponível. |

---

# 🇺🇸 English Documentation (EN)

## 📖 Overview & 100% Open Source Transparency

**Manager AI PRO** is a modern, safe, and interactive trilingual CLI tool that unifies environment setup, Frida `BillingClient` module injection, and subscription proration stacking for **Google AI Pro (5 TB)** using **[MuMuPlayer](https://www.mumuplayer.com/pt/)** (the **only** supported emulator) running Android 12 with Root.

### How It Works Under the Hood (No Secrets)

Google Play's billing backend serves hidden free-trial offer IDs for product SKU `g1.2tb.ai.subs_variant` (**Google AI Pro 5TB**) through `BillingClient.queryProductDetailsAsync`:

- **Step 1 (`pro12` / `12months-eft`):** Activates the initial **12-month free trial**.
- **Step 2 (`pro6` / `6months-eft`):** Stacks **+6 months** (totaling **18 months**).
- **Step 3 (`pro6b` / `6months-eft-2`):** Stacks **+6 months** (totaling **24 months**).
- **Backup (`pro6c` / `6months-eft-ss-2026`):** Backup **+6 months** offer (if a step above failed or to reach **30 months**).

To **stack** trial periods instead of replacing them, the script reads the active subscription's `purchaseToken` from `/data/data/com.android.vending/databases/library.db` and invokes `BillingFlowParams.SubscriptionUpdateParams` with `setReplaceProrationMode(5)` (`CHARGE_FULL_PRICE`). This instructs Google Play to prorate and defer your remaining trial balance while adding the new 6-month trial at **$0.00 due today**.

### 🚀 Quick Start

Double-click **`Manager AI PRO.bat`** or run:

```bash
python manager_ai_pro.py
```

1. Select your language (**PT-BR**, **English**, or **Chinese**) before the CLI loads.
2. Run **Option 1 (Install Environment)** — turns **GREEN** once Python, Frida `16.5.9`, and `adb` are ready.
3. Run **Option 2 (Prepare Environment)** — make sure you have **[MuMuPlayer](https://www.mumuplayer.com/pt/)** installed (the **only** supported emulator) with **ROOT enabled** and running **Android 12** (if on Android 15, uninstall the image and install Android 12), logged into your target Gmail account in Play Store, with the **Google One** app installed, and both **Play Store** and **Google One** kept open after a reboot. Confirm the highlighted prompt with your keyboard (`[✓ I UNDERSTAND]`).
4. Run **Options 3 → 4 → 5** in order (and **Option 6** if needed), accepting the **$0.00** checkout sheet inside MuMuPlayer on each step.

---

# 🇨🇳 中文文档 (ZH-CN)

## 📖 项目简介与 100% 开源透明说明

**Manager AI PRO** 是一款支持 **葡萄牙语 (PT-BR) / 英语 (EN) / 简体中文 (ZH-CN)** 的现代化交互式命令行管理工具，集成了环境安装、模拟器自检与 **Google AI Pro (5TB)** 免费试用叠加（最高累计 30 个月）的全套流程。本项目**唯一支持的模拟器为 [MuMu 模拟器 (MuMuPlayer)](https://www.mumuplayer.com/pt/)**。

### 核心原理（完全公开透明）

1. **商品与隐藏 Offer ID (`g1.2tb.ai.subs_variant`)：**
   - 第 1 步 (`pro12` / `12months-eft`)：开通 **12 个月免费试用**
   - 第 2 步 (`pro6` / `6months-eft`)：叠加 **+6 个月**（累计 18 个月）
   - 第 3 步 (`pro6b` / `6months-eft-2`)：叠加 **+6 个月**（累计 24 个月）
   - 备用包 (`pro6c` / `6months-eft-ss-2026`)：备用 **+6 个月**（若前面某步失败或继续叠加至 30 个月）
2. **订阅升级叠加机制：**
   - 脚本自动从 Play 商店数据库 `/data/data/com.android.vending/databases/library.db` 中读取当前活跃订阅的 `purchaseToken`，并通过 `BillingFlowParams.SubscriptionUpdateParams.setOldPurchaseToken(token).setReplaceProrationMode(5)`（`CHARGE_FULL_PRICE`）拉起 Play 收银台，从而将剩余试用期折算顺延，实现 0 元叠加。

### 🚀 快速启动

双击 **`Manager AI PRO.bat`** 或在终端运行：

```bash
python manager_ai_pro.py
```

1. 启动前可自由选择语言（**PT-BR / EN / 简体中文**）。
2. **1. 安装环境**：自动检查 Python、安装 `frida==16.5.9`、配置 `adb`，完成后菜单项变为**绿色**。
3. **2. 准备环境**：确保 **[MuMu 模拟器 (MuMuPlayer)](https://www.mumuplayer.com/pt/)**（唯一支持的模拟器）已开启 **ROOT 权限**，且系统镜像为 **Android 12**（若为 Android 15 请卸载并重装 Android 12 镜像），在 Play 商店登录目标谷歌账号并下载 **Google One**，重启模拟器后保持 **Play 商店** 和 **Google One** 处于打开状态。使用键盘方向键选择 `[✓ 我已了解]` 确认高亮提示后自动执行环境自检。
4. 依次执行 **3 → 4 → 5**（以及备用选项 **6**），每一步都会在 MuMu 模拟器中弹出收银台，在模拟器屏幕确认 0 元并点击订阅后即可进入下一步。

---

## 📂 Estrutura do Projeto / Project Structure / 目录结构

```text
Manager-AI-PRO/
├── Manager AI PRO.bat                 # Inicializador rápido Windows (1 clique)
├── manager_ai_pro.py                  # CLI Principal Trilíngue (PT-BR, EN, ZH-CN) com controle de etapas
├── ultra0.py                          # Motor principal de injeção Frida + BillingClient + ADB
├── setup_env.py                       # Script auxiliar de verificação de dependências
├── query_sku.py                       # Utilitário para inspecionar SKUs e Offers via Frida
├── instrucoes_de_uso.txt              # Guia rápido de uso
├── requirements.txt                   # Dependências Python (frida==16.5.9)
├── LICENSE                            # Licença Open Source MIT
└── README.md                          # Documentação completa Trilíngue
```

## 📄 Licença / License

Distribuído sob a licença **MIT Open Source**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
