#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                        ✦  M A N A G E R   A I   P R O  ✦
================================================================================
Unified Multilingual CLI Manager for Google AI Pro (5TB) Subscription Stacking
Supported Languages: Português (PT-BR), English (EN), 简体中文 (ZH-CN)
Supported Emulator : MuMuPlayer (https://www.mumuplayer.com/pt/) — Android 12 + Root
License            : MIT Open Source License

--------------------------------------------------------------------------------
ARCHITECTURAL CONSOLIDATION (ALL LEGACY .BAT & .TXT FILES UNIFIED HERE)
--------------------------------------------------------------------------------
This single file consolidates and replaces all 8 standalone legacy files:
  1. [instalar_ambiente_1_clique.bat] + [setup_env.py]
       -> Integrated into `run_step1_install_env()` (Menu Option 1)
       -> Checks Python 3.10+, installs frida==16.5.9, finds/downloads ADB,
          and connects to MuMuPlayer.
  2. [0_verificacao_ambiente.bat]
       -> Integrated into `run_step2_prepare_env()` (Menu Option 2)
       -> Command equivalent: `python ultra0.py --check`
  3. [1_ver_lista_ofertas.bat]
       -> Integrated into `run_list_offers()` (Menu Option O)
       -> Command equivalent: `python ultra0.py --account "current@device" --no-add --force --list --plan pro12`
  4. [2_Pro_12_meses_passo_1.bat]
       -> Integrated into `run_activation_step(..., step_num=3)` (Menu Option 3)
       -> Command equivalent: `python ultra0.py --account "current@device" --no-add --force --plan pro12`
  5. [3_Pro_mais_6_meses_passo_2.bat]
       -> Integrated into `run_activation_step(..., step_num=4)` (Menu Option 4)
       -> Command equivalent: `python ultra0.py --account "current@device" --no-add --force --stack --plan pro6`
  6. [4_Pro_mais_6_meses_passo_3.bat]
       -> Integrated into `run_activation_step(..., step_num=5)` (Menu Option 5)
       -> Command equivalent: `python ultra0.py --account "current@device" --no-add --force --stack --plan pro6b`
  7. [5_Pro_reserva_6_meses.bat]
       -> Integrated into `run_activation_step(..., step_num=6)` (Menu Option 6)
       -> Command equivalent: `python ultra0.py --account "current@device" --no-add --force --stack --plan pro6c`
  8. [instrucoes_de_uso.txt]
       -> Embedded and translated in full (PT-BR, EN, ZH-CN) inside `T[lang]["help_content"]`
          and rendered with rich ANSI color highlights via `render_colored_help()` (Menu Option 7).
================================================================================
"""

import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

# Enable ANSI escape sequences on Windows cmd/PowerShell
if os.name == "nt":
    os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / ".manager_state.json"
PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"

ADB_CANDIDATES = [
    os.environ.get("ADB_PATH", ""),
    r"C:\Program Files\Netease\MuMuPlayer-12.0\shell\adb.exe",
    r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\adb.exe",
    r"C:\Program Files (x86)\Netease\MuMuPlayer-12.0\shell\adb.exe",
    r"D:\Program Files\Netease\MuMu\nx_main\adb.exe",
    r"D:\Program Files\Netease\MuMu\nx_device\12.0\shell\adb.exe",
    r"C:\Program Files\Netease\MuMu\nx_main\adb.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"),
    os.path.expandvars(r"%USERPROFILE%\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
    str(BASE_DIR / "platform-tools" / "adb.exe"),
]


# ───────────────────────── ANSI Colors & Styling ─────────────────────────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def read_key() -> str:
    """Cross-platform single-keypress reader for interactive selectors."""
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            ch2 = msvcrt.getch()
            return {b"H": "UP", b"P": "DOWN", b"K": "LEFT", b"M": "RIGHT"}.get(ch2, "")
        if ch == b"\r":
            return "ENTER"
        if ch == b"\x1b":
            return "ESC"
        try:
            return ch.decode("utf-8", "ignore")
        except Exception:
            return ""
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                seq = sys.stdin.read(2)
                return {"[A": "UP", "[B": "DOWN", "[D": "LEFT", "[C": "RIGHT"}.get(seq, "ESC")
            if ch in ("\r", "\n"):
                return "ENTER"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ───────────────────────── State Persistence ─────────────────────────
DEFAULT_STATE = {
    "lang": None,
    "step1_installed": False,
    "step2_prepared": False,
    "step3_done": False,
    "step4_done": False,
    "step5_done": False,
    "step6_done": False,
}


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            st = dict(DEFAULT_STATE)
            st.update(data)
            return st
        except Exception:
            pass
    return dict(DEFAULT_STATE)


def save_state(state: dict):
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


# ───────────────────────── Runtime Output Translation ─────────────────────────
OUTPUT_TRANSLATIONS = {
    "pt": [
        ("环境自检通过，可以开始跑号了", "Verificação do ambiente concluída com sucesso! Tudo pronto para iniciar."),
        ("Play 商店进程在跑", "Processo da Google Play Store está em execução"),
        ("Play 商店没在跑，正在拉起…", "Play Store não está aberta, iniciando automaticamente..."),
        ("Play 商店已拉起", "Play Store iniciada com sucesso"),
        ("计费模块已就位", "Módulo de faturamento (BillingClient) pronto"),
        ("正在推送计费模块（一次性）…", "Enviando módulo de faturamento para o MuMuPlayer (única vez)..."),
        ("计费模块已推送", "Módulo de faturamento enviado com sucesso"),
        ("frida-server 已在运行", "frida-server já está em execução no MuMuPlayer"),
        ("frida-server 已启动", "frida-server iniciado com sucesso"),
        ("frida-server 启动失败", "Falha ao iniciar o frida-server"),
        ("设备上没有 frida-server，尝试用本地 frida 版本自动下载…", "frida-server ausente no MuMuPlayer; baixando versão compatível automaticamente..."),
        ("设备已连接：", "Dispositivo conectado: "),
        ("已连接模拟器", "MuMuPlayer conectado:"),
        ("没有检测到设备。MuMu 请确认已启动、开了 ADB 调试（设置里），或用 ADB_PATH 指定 adb。", "Nenhum dispositivo detectado. Confirme que o MuMuPlayer está aberto e com depuração ADB ativa."),
        ("已通过 adb root 提权", "Permissão Root obtida via adb root"),
        ("设备没有 root 权限。MuMu：设置里打开「ROOT 权限」并重启；或先手动执行 adb root。", "O MuMuPlayer não está com permissão ROOT! Ative o ROOT nas configurações do MuMuPlayer e reinicie."),
        ("注入计费模块，查询免费试用", "Injetando módulo BillingClient e consultando ofertas gratuitas..."),
        ("已拉起收银台：", "Tela de confirmação da oferta aberta no MuMuPlayer: "),
        ("检查收银台金额（只在 0 元时确认）", "Verificando valor na tela da Play Store (confirmação segura apenas se for 0)..."),
        ("已确认 0 元订阅", "Assinatura gratuita ($0) confirmada!"),
        ("已确认免费试用", "Teste gratuito confirmado!"),
        ("没有检测到收银台（可能这个号已经订阅过）", "Tela de pagamento não detectada automaticamente (verifique o MuMuPlayer manualmente)."),
        ("核对订阅状态", "Verificando status da assinatura na Google Play..."),
        ("正在读取当前订阅的 purchaseToken…", "Lendo purchaseToken da assinatura atual no library.db da Play Store..."),
        ("已读到 purchaseToken", "purchaseToken encontrado"),
        ("将用订阅升级模式叠加", "será utilizado o modo de upgrade (acumulação prorrateada)"),
        ("没读到 purchaseToken，将退回 queryPurchases 方式（可能拿不到）", "purchaseToken não lido do banco; tentando via queryPurchases..."),
        ("purchaseToken 来源账号：", "Conta de origem do purchaseToken: "),
        ("有效", "Válido/Ativo"),
        ("已过期", "Expirado"),
        ("已跳过 Play 账号校验（--force）", "Verificação automática de conta Play ignorada (--force)"),
        ("处理账号：", "Processando conta: "),
        ("共 1 个账号，开始执行", "Iniciando execução para a conta conectada no dispositivo"),
        ("进度", "Progresso"),
        ("结果：", "Resultado: "),
        ("汇总", "Resumo da Execução"),
        ("明细已保存到", "Relatório detalhado salvo em"),
        ("列表模式：使用设备当前账号", "Modo listagem: usando a conta atual do dispositivo"),
        ("（不校验、不下单）", "(sem validação extra, sem realizar pedido)"),
        ("未知", "desconhecida"),
        ("Play 提示：该账号不符合免费试用条件", "Aviso da Google Play: esta conta não é elegível para teste gratuito."),
    ],
    "en": [
        ("环境自检通过，可以开始跑号了", "Environment check passed! Ready to proceed."),
        ("Play 商店进程在跑", "Google Play Store process is running"),
        ("Play 商店没在跑，正在拉起…", "Play Store is not running, launching automatically..."),
        ("Play 商店已拉起", "Play Store launched successfully"),
        ("计费模块已就位", "BillingClient module is ready"),
        ("正在推送计费模块（一次性）…", "Pushing BillingClient module to MuMuPlayer (one-time)..."),
        ("计费模块已推送", "BillingClient module pushed"),
        ("frida-server 已在运行", "frida-server is already running"),
        ("frida-server 已启动", "frida-server started"),
        ("frida-server 启动失败", "frida-server failed to start"),
        ("设备上没有 frida-server，尝试用本地 frida 版本自动下载…", "frida-server not found on device; downloading matching version automatically..."),
        ("设备已连接：", "Device connected: "),
        ("已连接模拟器", "Connected to MuMuPlayer:"),
        ("没有检测到设备。MuMu 请确认已启动、开了 ADB 调试（设置里），或用 ADB_PATH 指定 adb。", "No device detected. Ensure MuMuPlayer is running with ADB debugging enabled."),
        ("已通过 adb root 提权", "Root privilege acquired via adb root"),
        ("设备没有 root 权限。MuMu：设置里打开「ROOT 权限」并重启；或先手动执行 adb root。", "Device does not have ROOT access! Enable ROOT permission in MuMuPlayer settings and restart."),
        ("注入计费模块，查询免费试用", "Injecting BillingClient module and querying free trial offers..."),
        ("已拉起收银台：", "Billing checkout sheet launched on MuMuPlayer: "),
        ("检查收银台金额（只在 0 元时确认）", "Checking checkout price (auto-confirming only if price is 0)..."),
        ("已确认 0 元订阅", "Confirmed $0 free subscription!"),
        ("已确认免费试用", "Confirmed free trial!"),
        ("没有检测到收银台（可能这个号已经订阅过）", "Checkout sheet not detected automatically (please check MuMuPlayer screen manually)."),
        ("核对订阅状态", "Verifying subscription status on Google Play..."),
        ("正在读取当前订阅的 purchaseToken…", "Reading current subscription purchaseToken from Play Store library.db..."),
        ("已读到 purchaseToken", "Found purchaseToken"),
        ("将用订阅升级模式叠加", "using subscription upgrade proration mode to stack"),
        ("没读到 purchaseToken，将退回 queryPurchases 方式（可能拿不到）", "purchaseToken not found in db; falling back to queryPurchases..."),
        ("purchaseToken 来源账号：", "purchaseToken source account: "),
        ("有效", "Active"),
        ("已过期", "Expired"),
        ("已跳过 Play 账号校验（--force）", "Skipped Play account switch verification (--force)"),
        ("处理账号：", "Processing account: "),
        ("共 1 个账号，开始执行", "Starting execution for current device account"),
        ("进度", "Progress"),
        ("结果：", "Result: "),
        ("汇总", "Execution Summary"),
        ("明细已保存到", "Detailed report saved to"),
        ("列表模式：使用设备当前账号", "List mode: using current device account"),
        ("（不校验、不下单）", "(no account switch, no purchase)"),
        ("未知", "unknown"),
        ("Play 提示：该账号不符合免费试用条件", "Google Play notice: this account is not eligible for the free trial."),
    ],
    "zh": [],
}


def translate_line(line: str, lang: str) -> str:
    if lang == "zh":
        return line
    for src, dst in OUTPUT_TRANSLATIONS.get(lang, []):
        if src in line:
            line = line.replace(src, dst)
    return line


# ───────────────────────── UI Translations Dictionary ─────────────────────────
T = {
    "pt": {
        "subtitle": "Gerenciador Oficial CLI · Google AI Pro (5TB) · Acumulação até 30 Meses",
        "status_ready": "CONCLUÍDO",
        "status_pending": "PENDENTE",
        "status_locked": "BLOQUEADO",
        "menu_header": "MENU PRINCIPAL",
        "opt1": "1. Instalar ambiente",
        "opt2": "2. Preparar ambiente",
        "opt3": "3. Ativar 12 Meses PRO (Passo 1)",
        "opt4": "4. (1) Ativar +6 Meses PRO (Passo 2 · Total 18m)",
        "opt5": "5. (2) Ativar +6 Meses PRO (Passo 3 · Total 24m)",
        "opt6": "6. Reserva +6 Meses (Caso alguma opção acima não tenha funcionado)",
        "opt7": "7. Ajuda (Instruções completas de uso)",
        "opt8": "8. Sair",
        "opt_lang": "L. Trocar Idioma / Change Language / 切换语言",
        "opt_list": "O. Consultar ofertas disponíveis na conta (Sem assinar / Risco Zero)",
        "prompt_choice": "Escolha uma opção e pressione [ENTER]: ",
        "invalid_choice": "Opção inválida! Tente novamente.",
        "press_enter": "\nPressione [ENTER] para voltar ao menu...",
        # Step 1 (Unified from instalar_ambiente_1_clique.bat & setup_env.py)
        "s1_title": "ETAPA 1: INSTALAÇÃO AUTOMÁTICA DO AMBIENTE",
        "s1_desc": (
            "Esta etapa irá preparar seu computador e o MuMuPlayer automaticamente:\n"
            "  • Verificar versão do Python (necessário 3.10+)\n"
            "  • Instalar Frida 16.5.9 (essencial para injeção Java Bridge)\n"
            "  • Localizar ou baixar automaticamente o ADB (Android Platform-Tools)\n"
            "  • Conectar ao MuMuPlayer e validar comunicação"
        ),
        "s1_check_py": "Verificando instalação do Python...",
        "s1_py_low": "Versão do Python muito antiga! Instale Python 3.10 ou superior em https://www.python.org/downloads/",
        "s1_py_ok": "Python compatível e pronto",
        "s1_frida": "Instalando / Verificando Frida 16.5.9 (obrigatório para injeção)...",
        "s1_frida_ok": "Frida instalado e pronto",
        "s1_frida_downgrade": "Detectado Frida 17.x (incompatível). Fazendo downgrade para 16.5.9...",
        "s1_frida_fail": "Falha ao instalar Frida. Execute manualmente: pip install frida==16.5.9",
        "s1_adb": "Procurando executável ADB...",
        "s1_adb_found": "ADB encontrado em",
        "s1_adb_dl": "ADB não encontrado. Baixando Android Platform-Tools oficial do Google...",
        "s1_adb_ready": "Platform-Tools extraído e pronto",
        "s1_emu": "Conectando ao emulador MuMuPlayer...",
        "s1_emu_none": "Nenhum MuMuPlayer conectado no momento. Certifique-se de abrir o MuMuPlayer antes da Etapa 2.",
        "s1_emu_ok": "Conectado ao MuMuPlayer",
        "s1_done": "Ambiente instalado com sucesso! A Opção 1 agora está marcada em VERDE no menu.",
        # Step 2 (Unified from 0_verificacao_ambiente.bat)
        "s2_warning_title": "⚠️  ATENÇÃO CRÍTICA — LEIA COM ATENÇÃO ANTES DE CONTINUAR  ⚠️",
        "s2_warning_lines": [
            "1. EMULADOR EXCLUSIVO (MuMuPlayer): O MuMuPlayer é o ÚNICO emulador suportado!",
            "   → Download oficial: https://www.mumuplayer.com/pt/",
            "   → Você PRECISA ativar a permissão ROOT nas configurações do MuMuPlayer.",
            "2. ANDROID 12 OBRIGATÓRIO: O MuMuPlayer PRECISA estar rodando o ANDROID 12.",
            "   → Caso esteja no Android 15 (ou outra versão), DESINSTALE a imagem atual e instale a imagem do Android 12!",
            "3. CONTA & APPS: Agora é a hora de:",
            "   • Logar na sua conta Gmail desejada na Google Play Store (com método de pagamento/cartão vinculado e sem assinatura ativa)",
            "   • Baixar e instalar o aplicativo oficial \"Google One\" na Play Store",
            "4. REINICIAR & MANTER ABERTO: Após instalar o Google One, REINICIE a emulação,",
            "   e deixe os aplicativos \"Google Play Store\" e \"Google One\" ABERTOS no MuMuPlayer!",
        ],
        "s2_accept_hint": "Use as setas [← / →] ou [↑ / ↓] para selecionar e pressione [ENTER] para confirmar:",
        "s2_btn_cancel": "[ Voltar ao Menu ]",
        "s2_btn_accept": "[ ✓ ENTENDI E JÁ CONFIGUREI TUDO ]",
        "s2_running": "Executando verificação completa do ambiente (ADB + Root + Frida Server + Billing Module + Play Store)...",
        "s2_success": "✅ AMBIENTE PREPARADO E VERIFICADO COM SUCESSO! O Passo 3 foi liberado.",
        "s2_failed": "❌ A verificação encontrou pendências. Verifique os avisos acima, ajuste o MuMuPlayer e tente novamente.",
        # Pre-activation warning
        "act_warn_title": "🔔 AVISO IMPORTANTE DE INJEÇÃO NO EMULADOR",
        "act_warn_body": (
            "O script irá injetar a chamada do módulo de faturamento diretamente no aplicativo Google One\n"
            "e abrirá uma tela da Google Play Store dentro do seu MuMuPlayer para aceitar a oferta.\n\n"
            "👉 É ESTRITAMENTE NECESSÁRIO ACEITAR A OFERTA NA TELA DO EMULADOR (verificando que o valor hoje é 0)\n"
            "   para que a assinatura seja ativada/acumulada e você possa avançar para a próxima etapa!"
        ),
        "act_btn_go": "[ ✓ ENTENDI, INJETAR OFERTA AGORA ]",
        "act_ask_accepted": "Você visualizou a tela no MuMuPlayer e ACEITOU a oferta gratuita com sucesso?",
        "act_yes": "[ ✓ SIM, ACEITEI A OFERTA COM SUCESSO ]",
        "act_no": "[ ✗ NÃO / DEU ERRO / TENTAR NOVAMENTE ]",
        "locked_msg2": "⚠️  Bloqueado! Você precisa concluir a opção '2. Preparar ambiente' com sucesso antes de ativar os 12 meses.",
        "locked_msg3": "⚠️  Bloqueado! Você precisa concluir a opção '3. Ativar 12 Meses PRO' e aceitar a oferta antes desta etapa.",
        "locked_msg4": "⚠️  Bloqueado! Você precisa concluir a opção '4. (1) Ativar +6 Meses PRO' e aceitar a oferta antes desta etapa.",
        "step_completed_ok": "✅ Etapa registrada como concluída com sucesso!",
        "step_not_completed": "⚠️  Etapa não confirmada. Você pode tentar novamente quando estiver pronto.",
        # Help text (Unified from instrucoes_de_uso.txt)
        "help_content": """================================================================================
   GUIA COMPLETO DE USO — MANAGER AI PRO (Google AI Pro 5TB · Até 30 Meses)
================================================================================

【ESCOPO SUPORTADO】
  Suporta exclusivamente Google AI Pro (5 TB):
    • Passo 1 (Opção 3): 12 meses de teste gratuito (12months-eft)
    • Passo 2 (Opção 4): Acumula +6 meses (6months-eft · totalizando 18 meses)
    • Passo 3 (Opção 5): Acumula +6 meses (6months-eft-2 · totalizando 24 meses)
    • Reserva (Opção 6): Pacote extra de +6 meses (6months-eft-ss-2026 · até 30 meses)
  Nota: Os planos Ultra (20TB / 30TB) foram removidos pois a Google não emite mais ofertas gratuitas para contas comuns.

【PRIMEIRO PASSO: INSTALAR AMBIENTE (APENAS UMA VEZ)】
  Execute a Opção 1 no menu principal:
    • Verifica o Python (necessário 3.10+)
    • Instala o Frida 16.5.9 (versões 17.x não funcionam e sofrem downgrade automático)
    • Localiza o ADB (Variável de ambiente → PATH → MuMuPlayer → ou baixa o platform-tools automaticamente)
    • Conecta ao MuMuPlayer e valida a comunicação

【PRÉ-REQUISITOS OBRIGATÓRIOS (TODOS ESSENCIAIS)】
  1. Emulador MuMuPlayer (ÚNICO EMULADOR SUPORTADO — https://www.mumuplayer.com/pt/) instalado com ANDROID 12
     ⚠️ Caso esteja no Android 15, DESINSTALE a imagem atual e instale a imagem do ANDROID 12!
  2. Permissão ROOT ativada nas configurações do MuMuPlayer e Depuração ADB ligada.
  3. Conta Google logada na Play Store com método de pagamento válido vinculado (cartão).
  4. A conta NÃO deve possuir nenhuma assinatura Google One pré-existente antes do Passo 1.
  5. App "Google One" instalado via Play Store. Após instalar, REINICIE o MuMuPlayer e deixe Play Store + Google One abertos.

【ORDEM DE EXECUÇÃO NO MENU】
  • 1. Instalar ambiente          → Configura Python, Frida 16.5.9 e ADB (fica VERDE quando concluído)
  • 2. Preparar ambiente          → Valida Android 12, Root, Frida-Server e Play Store (tudo verde para continuar)
  • O. Consultar ofertas          → Lista as ofertas gratuitas disponíveis na conta (sem assinar, risco zero)
  • 3. Ativar 12 Meses PRO        → 1ª ativação: 12 meses gratuitos (--plan pro12)
  • 4. (1) Ativar +6 Meses PRO    → 2ª ativação: soma +6 meses = 18 meses (--stack --plan pro6)
  • 5. (2) Ativar +6 Meses PRO    → 3ª ativação: soma +6 meses = 24 meses (--stack --plan pro6b)
  • 6. Reserva +6 Meses           → Pacote reserva: soma +6 meses extras (--stack --plan pro6c)

【COMO FUNCIONA A ACUMULAÇÃO (IMPORTANTE · 100% TRANSPARENTE)】
  Comprar diretamente apenas substituiria o plano mantendo a mesma data. Para somar os períodos,
  é obrigatório passar pelo fluxo de Upgrade de Assinatura da Google Play:

    1. O script lê automaticamente o `purchaseToken` da assinatura atual no arquivo `library.db` da Play Store
    2. Configura os parâmetros de atualização:
         BillingFlowParams.SubscriptionUpdateParams
           .setOldPurchaseToken(token_antigo)
           .setReplaceProrationMode(5)      // 5 = CHARGE_FULL_PRICE
    3. Abre a tela de confirmação (checkout) oficial da Google Play no MuMuPlayer.

  Como a tela de confirmação CORRETA deve aparecer no MuMuPlayer:
    • Valor cobrado hoje: 0 (R$ 0,00 / US$ 0.00 / JP¥ 0)
    • Período convertido: ex. 546 dias (incluindo 364 dias restantes convertidos do plano atual)
    • Data de início da primeira cobrança empurrada para frente (18 meses / 24 meses no futuro)

  ⚠️ Se a tela mostrar cobrança imediata ou a data não avançar:
    • Verifique se a assinatura atual está "Ativa" (assinaturas canceladas não permitem acumulação)
    • NÃO clique em assinar se o valor de hoje não for 0!

  Comandos manuais equivalentes (executados internamente pelo Manager AI PRO):
    python ultra0.py --account "current@device" --no-add --force --plan pro12
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6b
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6c

【IMPACTO DO STATUS DA ASSINATURA NA ACUMULAÇÃO】
  • A assinatura PRECISA estar "Ativa" (renovação automática ligada) para poder acumular.
  • Se estiver cancelada ("Cancelada / Assinar novamente"), novas compras viram renovação paga sem período gratuito.
  • Ordem correta: Confirmar assinatura ativa → Acumular todos os passos → Só cancelar DEPOIS de terminar tudo!
  • Após cancelar no final, seus benefícios permanecem ativos até a data final de vencimento.

【CONFERÊNCIA APÓS CADA ETAPA】
  Abra https://play.google.com/store/account/subscriptions e verifique a "Próxima data de pagamento":
    • Após Passo 1 (Opção 3) → 12 meses à frente
    • Após Passo 2 (Opção 4) → 18 meses à frente
    • Após Passo 3 (Opção 5) → 24 meses à frente
  Se a data avançou = acumulação bem-sucedida, pode ir para o próximo passo! Se não mudou = pare e verifique.

【SOLUÇÃO DE PROBLEMAS (TROUBLESHOOTING)】
  • Travado em "connecting":
      A Play Store não respondeu. Abra manualmente a Play Store e o Google One ou reinicie o MuMuPlayer.
  • "Você já é assinante":
      A conta já utilizou esse pacote de oferta específico, não sendo possível repetir o mesmo ID.
  • "Sem conexão com a internet":
      Oscilação de rede no emulador. Aguarde alguns segundos e tente novamente ou reinicie o MuMuPlayer.
  • "Invalid signature":
      Ocorre apenas no checkout web (que não aceita tokens Android). Sempre faça pelo script via Android Billing.
  • Valor no popup diferente de 0 / data não avançou:
      NÃO confirme! Feche o popup e verifique se a assinatura está ativa.

【AVISOS FINAIS DE SEGURANÇA】
  • Várias falhas seguidas acionam o controle de risco da Google (aguarde 24 horas antes de tentar novamente).
  • Lembre-se de cancelar a renovação automática antes do vencimento final para não ser cobrado após os 24/30 meses.
  • Recomendamos usar um cartão virtual com limite baixo para total segurança caso esqueça de cancelar no futuro.
================================================================================
""",
    },
    "en": {
        "subtitle": "Official CLI Manager · Google AI Pro (5TB) · Stack up to 30 Months",
        "status_ready": "COMPLETED",
        "status_pending": "PENDING",
        "status_locked": "LOCKED",
        "menu_header": "MAIN MENU",
        "opt1": "1. Install Environment",
        "opt2": "2. Prepare Environment",
        "opt3": "3. Activate 12 Months PRO (Step 1)",
        "opt4": "4. (1) Activate +6 Months PRO (Step 2 · Total 18m)",
        "opt5": "5. (2) Activate +6 Months PRO (Step 3 · Total 24m)",
        "opt6": "6. Backup +6 Months (If any option above did not work)",
        "opt7": "7. Help (Complete Usage Instructions)",
        "opt8": "8. Exit",
        "opt_lang": "L. Change Language / Trocar Idioma / 切换语言",
        "opt_list": "O. List available offers on account (No purchase / Zero Risk)",
        "prompt_choice": "Select an option and press [ENTER]: ",
        "invalid_choice": "Invalid option! Please try again.",
        "press_enter": "\nPress [ENTER] to return to the menu...",
        # Step 1
        "s1_title": "STEP 1: AUTOMATIC ENVIRONMENT INSTALLATION",
        "s1_desc": (
            "This step will automatically set up your PC and MuMuPlayer connection:\n"
            "  • Check Python version (requires 3.10+)\n"
            "  • Install Frida 16.5.9 (required for Java Bridge injection)\n"
            "  • Locate or automatically download ADB (Android Platform-Tools)\n"
            "  • Connect to MuMuPlayer and test communication"
        ),
        "s1_check_py": "Checking Python installation...",
        "s1_py_low": "Python version is too old! Please install Python 3.10+ from https://www.python.org/downloads/",
        "s1_py_ok": "Python is compatible and ready",
        "s1_frida": "Installing / Verifying Frida 16.5.9 (required for injection)...",
        "s1_frida_ok": "Frida is installed and ready",
        "s1_frida_downgrade": "Detected Frida 17.x (incompatible). Downgrading to 16.5.9...",
        "s1_frida_fail": "Failed to install Frida. Run manually: pip install frida==16.5.9",
        "s1_adb": "Searching for ADB executable...",
        "s1_adb_found": "Using ADB at",
        "s1_adb_dl": "ADB not found. Automatically downloading official Google Android Platform-Tools...",
        "s1_adb_ready": "Platform-Tools extracted and ready",
        "s1_emu": "Connecting to MuMuPlayer emulator...",
        "s1_emu_none": "No MuMuPlayer connected right now. Make sure to start MuMuPlayer before Step 2.",
        "s1_emu_ok": "Connected to MuMuPlayer",
        "s1_done": "Environment installed successfully! Option 1 is now highlighted in GREEN on the menu.",
        # Step 2
        "s2_warning_title": "⚠️  CRITICAL REQUIREMENT — READ CAREFULLY BEFORE CONTINUING  ⚠️",
        "s2_warning_lines": [
            "1. EXCLUSIVE EMULATOR (MuMuPlayer): MuMuPlayer is the ONLY supported emulator!",
            "   → Official download: https://www.mumuplayer.com/pt/",
            "   → You MUST enable ROOT permission in MuMuPlayer settings.",
            "2. ANDROID 12 REQUIRED: Your MuMuPlayer instance MUST be running ANDROID 12.",
            "   → If you are on Android 15 (or another version), UNINSTALL that image and install an Android 12 image!",
            "3. ACCOUNT & APPS: Now is the time to:",
            "   • Sign in to your target Gmail account in Google Play Store (with a payment card linked and no active Google One sub)",
            "   • Download and install the official \"Google One\" app from the Play Store",
            "4. RESTART & KEEP OPEN: After installing Google One, RESTART the MuMuPlayer instance,",
            "   and leave both \"Google Play Store\" and \"Google One\" OPEN on MuMuPlayer!",
        ],
        "s2_accept_hint": "Use arrow keys [← / →] or [↑ / ↓] to select and press [ENTER] to confirm:",
        "s2_btn_cancel": "[ Back to Menu ]",
        "s2_btn_accept": "[ ✓ I UNDERSTAND & COMPLETED ALL STEPS ]",
        "s2_running": "Running complete environment verification (ADB + Root + Frida Server + Billing Module + Play Store)...",
        "s2_success": "✅ ENVIRONMENT PREPARED AND VERIFIED SUCCESSFULLY! Step 3 is now unlocked.",
        "s2_failed": "❌ Verification found issues. Please review the messages above, fix MuMuPlayer setup, and try again.",
        # Pre-activation warning
        "act_warn_title": "🔔 IMPORTANT EMULATOR INJECTION NOTICE",
        "act_warn_body": (
            "The script will now inject a billing flow request directly into the Google One app\n"
            "and pop up a Google Play Store checkout sheet inside your MuMuPlayer to accept the offer.\n\n"
            "👉 IT IS STRICTLY NECESSARY TO ACCEPT THE OFFER ON THE EMULATOR SCREEN (verifying today's due is 0)\n"
            "   so the subscription is activated/stacked and you can proceed to the next step!"
        ),
        "act_btn_go": "[ ✓ I UNDERSTAND, INJECT OFFER NOW ]",
        "act_ask_accepted": "Did the checkout sheet appear on your MuMuPlayer and did you ACCEPT the free offer?",
        "act_yes": "[ ✓ YES, I ACCEPTED THE OFFER SUCCESSFULLY ]",
        "act_no": "[ ✗ NO / IT FAILED / TRY AGAIN LATER ]",
        "locked_msg2": "⚠️  Locked! You must complete '2. Prepare Environment' successfully before activating 12 Months PRO.",
        "locked_msg3": "⚠️  Locked! You must complete '3. Activate 12 Months PRO' and accept the offer before this step.",
        "locked_msg4": "⚠️  Locked! You must complete '4. (1) Activate +6 Months PRO' and accept the offer before this step.",
        "step_completed_ok": "✅ Step recorded as completed!",
        "step_not_completed": "⚠️  Step not marked as completed. You can retry anytime.",
        # Help text
        "help_content": """================================================================================
   COMPLETE USAGE GUIDE — MANAGER AI PRO (Google AI Pro 5TB · Up to 30 Months)
================================================================================

【SUPPORTED SCOPE】
  Exclusively supports Google AI Pro (5 TB):
    • Step 1 (Option 3): 12-month free trial (12months-eft)
    • Step 2 (Option 4): Stack +6 months (6months-eft · 18 months cumulative)
    • Step 3 (Option 5): Stack +6 months (6months-eft-2 · 24 months cumulative)
    • Backup (Option 6): Extra +6 months package (6months-eft-ss-2026 · up to 30 months)
  Note: Ultra (20TB / 30TB) tiers were removed as Google no longer issues trial offers to regular accounts.

【FIRST STEP: INSTALL ENVIRONMENT (ONCE ONLY)】
  Run Option 1 from the main menu:
    • Checks Python version (requires 3.10+)
    • Installs Frida 16.5.9 (17.x removed Java Bridge and will be automatically downgraded)
    • Finds ADB (ADB_PATH → PATH → MuMuPlayer built-in → or auto-downloads platform-tools)
    • Connects to MuMuPlayer and validates communication

【MANDATORY PREREQUISITES (ALL REQUIRED)】
  1. MuMuPlayer Emulator (THE ONLY SUPPORTED EMULATOR — https://www.mumuplayer.com/pt/) running ANDROID 12
     ⚠️ If you are on Android 15, UNINSTALL that image and install an ANDROID 12 system image!
  2. ROOT permission enabled in MuMuPlayer settings and ADB debugging active.
  3. Target Google account signed into Play Store with a valid payment method (card) bound.
  4. Account must NOT have any existing Google One subscription prior to Step 1.
  5. "Google One" app installed from Play Store. After installing, RESTART MuMuPlayer and keep Play Store + Google One open.

【EXECUTION ORDER IN MENU】
  • 1. Install Environment        → Sets up Python, Frida 16.5.9 & ADB (turns GREEN when done)
  • 2. Prepare Environment        → Verifies Android 12, Root, Frida-Server & Play Store
  • O. List available offers      → Checks which free offers exist on the account (no purchase, zero risk)
  • 3. Activate 12 Months PRO     → 1st activation: 12 months free (--plan pro12)
  • 4. (1) Activate +6 Months PRO → 2nd activation: adds +6 months = 18m (--stack --plan pro6)
  • 5. (2) Activate +6 Months PRO → 3rd activation: adds +6 months = 24m (--stack --plan pro6b)
  • 6. Backup +6 Months           → Backup package: adds +6 extra months (--stack --plan pro6c)

【HOW STACKING WORKS (IMPORTANT · 100% TRANSPARENT)】
  A direct purchase would simply replace the tier without extending the expiration date.
  Instead, this tool uses Google Play BillingClient's official Subscription Upgrade proration flow:

    1. Automatically reads your current subscription's `purchaseToken` from Play Store's `library.db`
    2. Configures `BillingFlowParams.SubscriptionUpdateParams`:
         .setOldPurchaseToken(old_token)
         .setReplaceProrationMode(5)      // 5 = CHARGE_FULL_PRICE
    3. Launches the official Play Store checkout sheet inside MuMuPlayer.

  How a successful stacking checkout sheet looks before clicking Subscribe:
    • Due today: 0 ($0.00 / JP¥0)
    • Prorated duration: e.g. 546 days (including 364 remaining days converted from your current plan)
    • Next billing start date pushed forward (18 months / 24 months into the future)

  ⚠️ If the sheet shows an immediate charge or the start date equals your current expiry date:
    • Check that your subscription is "Active" (canceled subscriptions cannot be stacked)
    • DO NOT click Subscribe if today's due amount is not 0!

  Equivalent manual commands (executed internally by Manager AI PRO):
    python ultra0.py --account "current@device" --no-add --force --plan pro12
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6b
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6c

【IMPACT OF SUBSCRIPTION STATUS ON STACKING】
  • Your subscription MUST remain "Active" (auto-renew enabled) while stacking.
  • If canceled early, Play treats new purchases as post-expiration paid renewals with no free trial period.
  • Correct order: Confirm active subscription → Complete all stacking steps → Cancel auto-renewal ONLY AFTER finishing!
  • After canceling, your benefits remain active until the final expiration date.

【VERIFY AFTER EACH STEP】
  Open https://play.google.com/store/account/subscriptions and check the "Next payment date":
    • After Step 1 (Option 3) → 12 months from today
    • After Step 2 (Option 4) → 18 months from today
    • After Step 3 (Option 5) → 24 months from today
  If the date moved forward = stacking succeeded, proceed to the next step! If unchanged = stop and check.

【TROUBLESHOOTING】
  • Stuck on "connecting":
      Play Store process isn't responding. Manually open Play Store and Google One or restart MuMuPlayer.
  • "You are already subscribed":
      Account already used this specific offer ID and cannot purchase it twice.
  • "No internet connection":
      Temporary emulator network drop. Wait a few seconds and retry, or restart MuMuPlayer.
  • "Invalid signature":
      Web checkout does not accept Android tokens. Orders must be placed via this script (Android Billing).
  • Popup amount is not 0 / date didn't advance:
      DO NOT click Subscribe! Close the sheet and check your subscription status.

【FINAL SAFETY NOTES】
  • Multiple consecutive failures may trigger Google risk control (wait 24 hours before retrying).
  • Remember to cancel auto-renewal before the final expiration date to avoid being charged.
  • Using a virtual card with a low spending limit is recommended in case you forget to cancel.
================================================================================
""",
    },
    "zh": {
        "subtitle": "官方 CLI 管理器 · Google AI Pro (5TB) · 免费试用叠加至最高 30 个月",
        "status_ready": "已完成",
        "status_pending": "待执行",
        "status_locked": "未解锁",
        "menu_header": "主菜单 (MAIN MENU)",
        "opt1": "1. 安装环境 (一键配置 Python / Frida 16.5.9 / ADB)",
        "opt2": "2. 准备环境 (模拟器 Android 12 + Root 检查与自检)",
        "opt3": "3. 激活 12 个月 PRO (第 1 步)",
        "opt4": "4. (1) 叠加 +6 个月 PRO (第 2 步 · 累计 18 个月)",
        "opt5": "5. (2) 叠加 +6 个月 PRO (第 3 步 · 累计 24 个月)",
        "opt6": "6. 备用 +6 个月 (若上方某一步未生效或继续叠加)",
        "opt7": "7. 帮助说明 (完整使用说明与原理解析)",
        "opt8": "8. 退出程序",
        "opt_lang": "L. 切换语言 / Trocar Idioma / Change Language",
        "opt_list": "O. 查看当前账号可用 Offer 列表 (不下单 · 零风险)",
        "prompt_choice": "请输入选项编号并按 [回车]: ",
        "invalid_choice": "无效选项，请重新输入！",
        "press_enter": "\n按 [回车键] 返回主菜单...",
        # Step 1
        "s1_title": "第 1 步：一键安装运行环境",
        "s1_desc": (
            "本步骤将自动完成以下环境配置：\n"
            "  • 检查 Python 版本（需 3.10+）\n"
            "  • 安装 frida 16.5.9（17.x 移除了 Java Bridge，会自动降级）\n"
            "  • 查找或自动下载官方 Android Platform-Tools (adb)\n"
            "  • 连接 MuMu 模拟器并测试通信"
        ),
        "s1_check_py": "正在检查 Python 环境...",
        "s1_py_low": "Python 版本过低！请前往 https://www.python.org/downloads/ 安装 3.10 或更高版本",
        "s1_py_ok": "Python 版本可用",
        "s1_frida": "正在安装 / 检查 frida 16.5.9（脚本注入必需）...",
        "s1_frida_ok": "frida 已就绪",
        "s1_frida_downgrade": "检测到 frida 17.x（不兼容），正在降级至 16.5.9…",
        "s1_frida_fail": "frida 安装失败，请手动执行：pip install frida==16.5.9",
        "s1_adb": "正在查找 adb 工具...",
        "s1_adb_found": "使用 adb：",
        "s1_adb_dl": "未找到 adb，正在自动下载官方 platform-tools...",
        "s1_adb_ready": "platform-tools 解压就绪",
        "s1_emu": "正在连接 MuMu 模拟器...",
        "s1_emu_none": "暂未检测到运行中的 MuMu 模拟器。请在进入第 2 步前启动模拟器。",
        "s1_emu_ok": "已连接 MuMu 模拟器",
        "s1_done": "环境安装完成！主菜单中的选项 1 已变为绿色就绪状态。",
        # Step 2
        "s2_warning_title": "⚠️  重要前置提示 —— 继续前请仔细阅读  ⚠️",
        "s2_warning_lines": [
            "1. 唯一支持模拟器 (MuMuPlayer)：仅支持使用【MuMu 模拟器 (MuMuPlayer)】！",
            "   → 官方下载地址：https://www.mumuplayer.com/pt/",
            "   → 必须在 MuMu 模拟器设置中开启【ROOT 权限】。",
            "2. 必须使用 ANDROID 12：MuMu 模拟器镜像版本必须为【Android 12】。",
            "   → 如果当前是 Android 15（或其它版本），请卸载当前镜像并重新安装 Android 12 镜像！",
            "3. 登录账号与安装应用：现在请在模拟器中完成：",
            "   • 在 Google Play 商店登录目标 Gmail 账号（已绑卡，且当前没有任何 Google One 订阅）",
            "   • 在 Play 商店搜索并下载安装「Google One」应用",
            "4. 重启并保持打开：安装完 Google One 后，请【重启 MuMu 模拟器】，",
            "   重启后打开「Play 商店」和「Google One」并保持在后台/前台运行！",
        ],
        "s2_accept_hint": "请使用方向键 [← / →] 或 [↑ / ↓] 选择「我已了解」并按 [回车] 确认：",
        "s2_btn_cancel": "[ 返回主菜单 ]",
        "s2_btn_accept": "[ ✓ 我已了解并已完成上述配置 ]",
        "s2_running": "正在执行环境自检（检查 ADB / Root / Frida-Server / 计费模块 / Play 商店进程）...",
        "s2_success": "✅ 环境准备与自检全部通过！已解锁第 3 步。",
        "s2_failed": "❌ 环境自检未通过，请根据上方提示检查 MuMu 模拟器配置后重试。",
        # Pre-activation warning
        "act_warn_title": "🔔 模拟器收银台弹窗重要提示",
        "act_warn_body": (
            "脚本即将向 MuMu 模拟器内的 Google One 进程注入计费请求，并在模拟器屏幕上拉起 Google Play 收银台弹窗。\n\n"
            "👉 请务必查看模拟器屏幕，确认今日扣款金额为 0 后，在模拟器中点击【订阅 / 接受优惠】！\n"
            "   只有成功接受优惠后，才能继续执行下一步叠加！"
        ),
        "act_btn_go": "[ ✓ 我已了解，立即拉起模拟器收银台 ]",
        "act_ask_accepted": "MuMu 模拟器中是否已弹出收银台，并且您已成功点击【订阅/接受】？",
        "act_yes": "[ ✓ 是的，我已成功接受优惠 ]",
        "act_no": "[ ✗ 否 / 未弹出或失败，稍后重试 ]",
        "locked_msg2": "⚠️  未解锁！请先完成「2. 准备环境」并通过自检后，再执行本步骤。",
        "locked_msg3": "⚠️  未解锁！请先完成「3. 激活 12 个月 PRO」并在模拟器中接受优惠后，再执行本步骤。",
        "locked_msg4": "⚠️  未解锁！请先完成「4. (1) 叠加 +6 个月 PRO」并在模拟器中接受优惠后，再执行本步骤。",
        "step_completed_ok": "✅ 当前步骤已标记为成功完成！",
        "step_not_completed": "⚠️  当前步骤未确认完成，您可以随时重新执行。",
        # Help text (Unified from 使用说明.txt / instrucoes_de_uso.txt)
        "help_content": """================================================================================
   Google AI Pro 一键开通 / 叠加（MuMu 模拟器版 · 完整使用说明）
================================================================================

【支持范围】
  只支持 Google AI Pro (5 TB)
    • 第 1 步（选项 3）：12 个月免费试用 (12months-eft)
    • 第 2 步（选项 4）：叠加 6 个月 (6months-eft · 累计 18 个月)
    • 第 3 步（选项 5）：再叠加 6 个月 (6months-eft-2 · 累计 24 个月)
    • 备用包（选项 6）：还能再叠 6 个月 (6months-eft-ss-2026 · 最多 30 个月)
  Ultra（20TB / 30TB）已移除：官方已不向普通账号下发试用 offer。

【第一步：装环境（只需一次）】
  在主菜单选择「1. 安装环境」，自动完成：
    1. 检查 Python（需 3.10+）
    2. 安装 frida 16.5.9（17.x 不能用，会自动降级）
    3. 找 adb（环境变量 → PATH → MuMu 自带 → 都没有就自动下载 platform-tools）
    4. 连接 MuMu 模拟器并验证通信

【前提（缺一不可）】
  1. 唯一支持模拟器：MuMu 模拟器 (https://www.mumuplayer.com/pt/)，必须使用 ANDROID 12 镜像
     ⚠️ 如果是 Android 15，请卸载当前镜像并重新安装 ANDROID 12 镜像！
  2. 在 MuMu 模拟器设置中开启【ROOT 权限】及 ADB 调试
  3. 已在 Play 商店登录目标 Google 账号，且该账号已绑定付款方式（卡）
  4. 该账号没有任何现存 Google One 订阅
  5. 在 Play 商店下载安装「Google One」应用，重启模拟器后保持 Play 商店与 Google One 处于打开状态

【菜单执行顺序】
  • 1. 安装环境                  → 自动配置 Python / Frida 16.5.9 / ADB（完成后变绿）
  • 2. 准备环境                  → 环境自检，全绿后解锁下一步
  • O. 查看可用 Offer 列表       → 看当前账号有哪些免费档（不下单，零风险）
  • 3. 激活 12 个月 PRO          → 第 1 次：12 个月免费 (--plan pro12)
  • 4. (1) 叠加 +6 个月 PRO      → 第 2 次：再 +6 个月（18 个月）(--stack --plan pro6)
  • 5. (2) 叠加 +6 个月 PRO      → 第 3 次：再 +6 个月（24 个月）(--stack --plan pro6b)
  • 6. 备用 +6 个月              → 备用包（前三步都成功后再用，或某步失败时替补）(--stack --plan pro6c)

【叠加是怎么实现的（重要 · 100% 透明）】
  直接下单只会「换成同档、日期不变」，必须走 Play 的订阅升级：

    1. 从 Play 的 library.db 读出当前订阅的 purchaseToken（脚本已自动读取，不用你填）
    2. BillingFlowParams.SubscriptionUpdateParams
         .setOldPurchaseToken(旧 token)
         .setReplaceProrationMode(5)      // 5 = CHARGE_FULL_PRICE
    3. 再拉起收银台

  叠加成功的收银台长这样（这就是对的）：
    • 即将扣款：今天 JP¥0 / US$0.00
    • 546 天（包含根据您的当前方案所剩时间折算出的 364 天）
    • 开始日期往后顺延（18 个月 / 24 个月后才收取第一笔费用）

  ⚠️ 如果显示的是「开始日期 = 当前到期日、当天就扣费」，说明没走升级模式：
    • 检查订阅是否处于「活跃」状态（已取消的订阅不给叠加）
    • 弹窗金额不是 0 时千万不要点订阅！

  手动命令（等价于菜单各步骤）：
    python ultra0.py --account "current@device" --no-add --force --plan pro12
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6b
    python ultra0.py --account "current@device" --no-add --force --stack --plan pro6c

【订阅状态对叠加的影响】
  • 订阅必须「活跃」（自动续订开着）才能叠加
  • 已取消（显示「已取消 / 重新订阅」）时，新购买会被当成「到期后转付费」，不给试用期
  • 所以顺序是：先确认订阅活跃 → 叠加 → 全部叠完再取消订阅
  • 取消后权益保留到到期日，不会提前失效

【每一步之后要核对】
  打开 https://play.google.com/store/account/subscriptions 看「下次付款日期」：
    • 第 1 步后 → 12 个月后
    • 第 2 步后 → 18 个月后
    • 第 3 步后 → 24 个月后
  日期往后推 = 叠加成功，可以继续下一步；没变 = 停手检查。

【排错】
  • 卡在 connecting：
      Play 商店没起来。手动打开 Play 商店与 Google One 或重启 MuMu 模拟器。
  • 您已订阅：
      该账号已有该档订阅，不能重复购买同一 offerId。
  • 未连接到互联网：
      模拟器网络瞬断。等几秒重试；频繁出现就重启模拟器。
  • Invalid signature：
      这是网页端的问题（网页结账不认 Android 的 token）。下单只能走本脚本（Android Billing）。
  • 弹窗金额不是 0 / 日期没往后推：
      不要点订阅，直接关掉，检查订阅状态与 --stack 参数。

【注意】
  • 连续失败多次会触发风控，隔 24 小时再试
  • 到期前记得取消订阅，否则到期后按月自动扣费
  • 建议用额度较低的卡，万一忘记取消也扣不动
================================================================================
""",
    },
}


# ───────────────────────── Interactive UI Widgets ─────────────────────────
def print_banner(lang: str):
    sub = T[lang]["subtitle"] if lang in T else "Português (PT-BR) · English (EN) · 中文 (ZH-CN)"
    print(f"{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║                                                                              ║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║{C.WHITE}                        ✦  M A N A G E R   A I   P R O  ✦                     {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║                                                                              ║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
    print(f"  {C.YELLOW}{C.BOLD}{sub}{C.RESET}\n")


def select_language(current_lang: str | None = None) -> str:
    options = [
        ("pt", "🇧🇷  Português (Brasil) — PT-BR"),
        ("en", "🇺🇸  English            — EN"),
        ("zh", "🇨🇳  简体中文           — ZH-CN"),
    ]
    idx = 0
    if current_lang:
        for i, (code, _) in enumerate(options):
            if code == current_lang:
                idx = i
                break

    while True:
        clear_screen()
        print_banner(options[idx][0])
        print(f"  {C.BOLD}Selecione o idioma / Select language / 请选择语言:{C.RESET}")
        print(f"  {C.DIM}(Use ↑/↓ ou 1-3 e pressione ENTER){C.RESET}\n")
        for i, (code, label) in enumerate(options):
            if i == idx:
                print(f"    {C.BG_BLUE}{C.WHITE}{C.BOLD}  ▶ {i + 1}. {label}  {C.RESET}")
            else:
                print(f"       {i + 1}. {label}")
        print()
        k = read_key()
        if k in ("UP", "LEFT", "w", "W"):
            idx = (idx - 1) % len(options)
        elif k in ("DOWN", "RIGHT", "s", "S"):
            idx = (idx + 1) % len(options)
        elif k in ("1", "2", "3"):
            return options[int(k) - 1][0]
        elif k == "ENTER":
            return options[idx][0]


def interactive_confirm_box(
    lang: str,
    title: str,
    lines: list[str],
    btn_cancel: str,
    btn_accept: str,
    default_accept: bool = False,
    border_color: str = C.YELLOW,
) -> bool:
    """Renders a high-visibility colored box requiring explicit keyboard selection of 'Understood'."""
    selected = 1 if default_accept else 0  # 0 = cancel, 1 = accept
    while True:
        clear_screen()
        print_banner(lang)
        print(f"{border_color}{C.BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{C.RESET}")
        print(f"{border_color}{C.BOLD}┃ {C.BG_RED}{C.WHITE} {title} {C.RESET}")
        print(f"{border_color}{C.BOLD}┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫{C.RESET}")
        for ln in lines:
            up = ln.upper()
            if any(k in up for k in ("ANDROID 12", "ROOT", "MUMUPLAYER", "NECESS", "STRICTLY", "务必", "唯一")):
                print(f"{border_color}{C.BOLD}┃ {C.YELLOW}{C.BOLD}{ln}{C.RESET}")
            else:
                print(f"{border_color}{C.BOLD}┃ {C.WHITE}{ln}{C.RESET}")
        print(f"{border_color}{C.BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{C.RESET}\n")

        print(f"  {C.CYAN}{T[lang]['s2_accept_hint']}{C.RESET}\n")

        if selected == 0:
            b0 = f"{C.BG_RED}{C.WHITE}{C.BOLD}  ▶ {btn_cancel}  {C.RESET}"
            b1 = f"{C.DIM}    {btn_accept}  {C.RESET}"
        else:
            b0 = f"{C.DIM}    {btn_cancel}  {C.RESET}"
            b1 = f"{C.BG_GREEN}{C.WHITE}{C.BOLD}  ▶ {btn_accept}  {C.RESET}"

        print(f"    {b0}      {b1}\n")

        k = read_key()
        if k in ("LEFT", "UP", "a", "A", "1"):
            selected = 0
        elif k in ("RIGHT", "DOWN", "d", "D", "2"):
            selected = 1
        elif k == "ESC":
            return False
        elif k == "ENTER":
            return selected == 1


def render_colored_help(text: str):
    """Applies rich ANSI color styling to the help instructions (Option 7)."""
    for raw_line in text.splitlines():
        s = raw_line.strip()
        if s.startswith("==="):
            print(f"{C.CYAN}{C.BOLD}{raw_line}{C.RESET}")
        elif "GUIA COMPLETO" in raw_line or "COMPLETE USAGE GUIDE" in raw_line or "一键开通" in raw_line:
            print(f"{C.WHITE}{C.BOLD}{raw_line}{C.RESET}")
        elif s.startswith("【") and "】" in s:
            print(f"\n{C.BG_BLUE}{C.WHITE}{C.BOLD}  {s}  {C.RESET}")
        elif "⚠️" in raw_line or "NÃO " in raw_line or "DO NOT" in raw_line or "不要" in raw_line or "千万不要" in raw_line:
            print(f"{C.RED}{C.BOLD}{raw_line}{C.RESET}")
        elif "python ultra0.py" in raw_line or ".setOldPurchaseToken" in raw_line or ".setReplaceProrationMode" in raw_line or "BillingFlowParams" in raw_line:
            print(f"{C.GREEN}{C.BOLD}{raw_line}{C.RESET}")
        elif s.startswith("•") or s.startswith("·"):
            # Highlight step bullets and arrows
            colored = raw_line
            colored = re.sub(
                r"(https?://[^\s)]+)",
                f"{C.CYAN}{C.BOLD}\\1{C.RESET}{C.WHITE}",
                colored,
            )
            colored = re.sub(
                r"(ANDROID 12|ROOT|MuMuPlayer|12months-eft|6months-eft-ss-2026|6months-eft-2|6months-eft|VERDE|GREEN)",
                f"{C.YELLOW}{C.BOLD}\\1{C.RESET}{C.WHITE}",
                colored,
            )
            if "→" in colored:
                parts = colored.split("→", 1)
                print(f"{C.CYAN}{C.BOLD}{parts[0]}→{C.WHITE}{parts[1]}{C.RESET}")
            else:
                print(f"{C.WHITE}{colored}{C.RESET}")
        elif re.match(r"^\d+\.", s):
            colored = re.sub(
                r"(https?://[^\s)]+)",
                f"{C.CYAN}{C.BOLD}\\1{C.RESET}{C.YELLOW}",
                raw_line,
            )
            print(f"{C.YELLOW}{C.BOLD}{colored}{C.RESET}")
        else:
            colored = re.sub(
                r"(https?://[^\s)]+)",
                f"{C.CYAN}{C.BOLD}\\1{C.RESET}",
                raw_line,
            )
            print(f"{C.WHITE}{colored}{C.RESET}")


# ───────────────────────── Core Step Runners ─────────────────────────
def find_or_download_adb(lang: str) -> str:
    t = T[lang]
    print(f"\n{C.CYAN}▶ {t['s1_adb']}{C.RESET}")
    for c in ADB_CANDIDATES:
        if not c:
            continue
        if c in ("adb", "adb.exe"):
            continue
        if Path(c).exists():
            print(f"   {C.GREEN}✅ {t['s1_adb_found']}: {c}{C.RESET}")
            return c
    w = shutil.which("adb")
    if w:
        print(f"   {C.GREEN}✅ {t['s1_adb_found']} (PATH): {w}{C.RESET}")
        return w

    print(f"   {C.YELLOW}⚠️  {t['s1_adb_dl']}{C.RESET}")
    dest = BASE_DIR / "platform-tools"
    tmp = Path(tempfile.gettempdir()) / "platform-tools.zip"
    with urllib.request.urlopen(PLATFORM_TOOLS_URL, timeout=180) as r, open(tmp, "wb") as f:
        f.write(r.read())
    with zipfile.ZipFile(tmp) as z:
        z.extractall(BASE_DIR)
    tmp.unlink(missing_ok=True)
    adb = dest / "adb.exe"
    if adb.exists():
        print(f"   {C.GREEN}✅ {t['s1_adb_ready']}: {adb}{C.RESET}")
        return str(adb)
    raise RuntimeError("adb.exe not found after extracting platform-tools")


def run_step1_install_env(state: dict):
    """
    Replaces and unifies `instalar_ambiente_1_clique.bat` and `setup_env.py`.
    Checks Python 3.10+, installs frida==16.5.9, locates/downloads ADB, and connects to MuMuPlayer.
    """
    lang = state["lang"]
    t = T[lang]
    clear_screen()
    print_banner(lang)
    print(f"{C.CYAN}{C.BOLD}════════════════════════════════════════════════════════════════════════════════{C.RESET}")
    print(f"  {C.WHITE}{C.BOLD}{t['s1_title']}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}════════════════════════════════════════════════════════════════════════════════{C.RESET}")
    print(f"{t['s1_desc']}\n")

    # 1. Check Python
    print(f"{C.CYAN}▶ {t['s1_check_py']}{C.RESET}")
    print(f"   Python {platform.python_version()} ({platform.architecture()[0]})")
    if sys.version_info < (3, 9):
        print(f"   {C.RED}❌ {t['s1_py_low']}{C.RESET}")
        input(t["press_enter"])
        return
    print(f"   {C.GREEN}✅ {t['s1_py_ok']}{C.RESET}")

    # 2. Install/check Frida 16.5.9
    print(f"\n{C.CYAN}▶ {t['s1_frida']}{C.RESET}")
    frida_ok = False
    try:
        import frida
        if frida.__version__.startswith("16."):
            print(f"   {C.GREEN}✅ {t['s1_frida_ok']} (v{frida.__version__}){C.RESET}")
            frida_ok = True
        else:
            print(f"   {C.YELLOW}⚠️  {t['s1_frida_downgrade']} (v{frida.__version__}){C.RESET}")
    except Exception:
        pass

    if not frida_ok:
        cmds = [
            [sys.executable, "-m", "pip", "install", "--no-cache-dir", "frida==16.5.9"],
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "-i",
                "https://pypi.tuna.tsinghua.edu.cn/simple",
                "frida==16.5.9",
            ],
        ]
        for c in cmds:
            print(f"   {C.DIM}$ {' '.join(c[2:])}{C.RESET}")
            r = subprocess.run(c, capture_output=True, text=True, errors="ignore")
            if r.returncode == 0:
                frida_ok = True
                break
        if frida_ok:
            print(f"   {C.GREEN}✅ {t['s1_frida_ok']} (v16.5.9){C.RESET}")
        else:
            print(f"   {C.RED}❌ {t['s1_frida_fail']}{C.RESET}")
            input(t["press_enter"])
            return

    # 3. Find or download ADB
    try:
        adb = find_or_download_adb(lang)
        os.environ["ADB_PATH"] = adb
    except Exception as e:
        print(f"   {C.RED}❌ ADB Error: {e}{C.RESET}")
        input(t["press_enter"])
        return

    # 4. Try connecting to MuMuPlayer ADB ports
    print(f"\n{C.CYAN}▶ {t['s1_emu']}{C.RESET}")
    ports = ["16384", "7555", "16416", "21503", "62001", "5555"]
    for p in ports:
        try:
            subprocess.run([adb, "connect", f"127.0.0.1:{p}"], capture_output=True, text=True, timeout=6)
        except Exception:
            pass
    out = subprocess.run([adb, "devices"], capture_output=True, text=True, errors="ignore").stdout
    devices = [l.split("\t")[0] for l in out.splitlines()[1:] if "\tdevice" in l]
    if devices:
        print(f"   {C.GREEN}✅ {t['s1_emu_ok']}: {', '.join(devices)}{C.RESET}")
    else:
        print(f"   {C.YELLOW}⚠️  {t['s1_emu_none']}{C.RESET}")

    state["step1_installed"] = True
    save_state(state)
    print(f"\n{C.BG_GREEN}{C.WHITE}{C.BOLD}  ✅ {t['s1_done']}  {C.RESET}")
    input(t["press_enter"])


def run_ultra0_translated(args: list[str], lang: str) -> tuple[int, str]:
    """Runs ultra0.py with real-time translated output streaming."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    for c in ADB_CANDIDATES:
        if c and c not in ("adb", "adb.exe") and Path(c).exists():
            env["ADB_PATH"] = c
            break

    cmd = [sys.executable, str(BASE_DIR / "ultra0.py")] + args
    proc = subprocess.Popen(
        cmd,
        cwd=str(BASE_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    full_out = []
    assert proc.stdout is not None
    for raw_line in proc.stdout:
        line = raw_line.rstrip("\r\n")
        t_line = translate_line(line, lang)
        full_out.append(t_line)
        if "✅" in t_line:
            print(f"{C.GREEN}{t_line}{C.RESET}")
        elif "⚠️" in t_line:
            print(f"{C.YELLOW}{t_line}{C.RESET}")
        elif "❌" in t_line:
            print(f"{C.RED}{C.BOLD}{t_line}{C.RESET}")
        elif t_line.startswith("▶"):
            print(f"{C.CYAN}{C.BOLD}{t_line}{C.RESET}")
        else:
            print(t_line)
    proc.wait()
    return proc.returncode, "\n".join(full_out)


def check_android_version_notice(lang: str):
    """Queries Android SDK / Release version via ADB if connected and displays helpful feedback."""
    adb = os.environ.get("ADB_PATH") or shutil.which("adb")
    if not adb:
        for c in ADB_CANDIDATES:
            if c and Path(c).exists():
                adb = c
                break
    if not adb:
        return
    try:
        rel = subprocess.run(
            [adb, "shell", "getprop", "ro.build.version.release"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        if rel:
            if rel.startswith("12"):
                msg = {
                    "pt": f"   ✅ Versão do Android detectada no MuMuPlayer: Android {rel} (Compatível!)",
                    "en": f"   ✅ Detected Android version on MuMuPlayer: Android {rel} (Compatible!)",
                    "zh": f"   ✅ 检测到 MuMu 模拟器 Android 版本：Android {rel}（版本正确！）",
                }[lang]
                print(f"{C.GREEN}{C.BOLD}{msg}{C.RESET}")
            else:
                msg = {
                    "pt": f"   ⚠️  ATENÇÃO: MuMuPlayer reportou Android {rel}! Desinstale a imagem atual e instale o ANDROID 12!",
                    "en": f"   ⚠️  WARNING: MuMuPlayer reported Android {rel}! Please uninstall this image and use ANDROID 12!",
                    "zh": f"   ⚠️  警告：检测到 MuMu 模拟器为 Android {rel}！请卸载当前镜像并更换为 Android 12！",
                }[lang]
                print(f"{C.BG_RED}{C.WHITE}{C.BOLD}{msg}{C.RESET}")
    except Exception:
        pass


def run_step2_prepare_env(state: dict):
    """
    Replaces and unifies `0_verificacao_ambiente.bat` (`python ultra0.py --check`).
    Requires user keyboard confirmation of the MuMuPlayer Android 12 + Root + Google One setup first.
    """
    lang = state["lang"]
    t = T[lang]
    accepted = interactive_confirm_box(
        lang=lang,
        title=t["s2_warning_title"],
        lines=t["s2_warning_lines"],
        btn_cancel=t["s2_btn_cancel"],
        btn_accept=t["s2_btn_accept"],
        default_accept=True,
        border_color=C.YELLOW,
    )
    if not accepted:
        return

    clear_screen()
    print_banner(lang)
    print(f"{C.CYAN}{C.BOLD}▶ {t['s2_running']}{C.RESET}\n")
    check_android_version_notice(lang)
    code, _ = run_ultra0_translated(["--check"], lang)
    print()
    if code == 0:
        state["step1_installed"] = True
        state["step2_prepared"] = True
        save_state(state)
        print(f"{C.BG_GREEN}{C.WHITE}{C.BOLD}  {t['s2_success']}  {C.RESET}")
    else:
        print(f"{C.BG_RED}{C.WHITE}{C.BOLD}  {t['s2_failed']}  {C.RESET}")
    input(t["press_enter"])


def run_activation_step(state: dict, step_num: int, plan_args: list[str], state_key: str):
    """
    Replaces and unifies:
      - Step 3: `2_Pro_12_meses_passo_1.bat`     (--plan pro12)
      - Step 4: `3_Pro_mais_6_meses_passo_2.bat` (--stack --plan pro6)
      - Step 5: `4_Pro_mais_6_meses_passo_3.bat` (--stack --plan pro6b)
      - Step 6: `5_Pro_reserva_6_meses.bat`      (--stack --plan pro6c)
    """
    lang = state["lang"]
    t = T[lang]

    # Prerequisite gates
    if step_num == 3 and not state.get("step2_prepared"):
        print(f"\n{C.BG_RED}{C.WHITE}{C.BOLD}  {t['locked_msg2']}  {C.RESET}")
        input(t["press_enter"])
        return
    if step_num == 4 and not state.get("step3_done"):
        print(f"\n{C.BG_RED}{C.WHITE}{C.BOLD}  {t['locked_msg3']}  {C.RESET}")
        input(t["press_enter"])
        return
    if step_num == 5 and not state.get("step4_done"):
        print(f"\n{C.BG_RED}{C.WHITE}{C.BOLD}  {t['locked_msg4']}  {C.RESET}")
        input(t["press_enter"])
        return

    # Show mandatory pre-injection confirmation screen
    body_lines = t["act_warn_body"].splitlines()
    go = interactive_confirm_box(
        lang=lang,
        title=t["act_warn_title"],
        lines=body_lines,
        btn_cancel=t["s2_btn_cancel"],
        btn_accept=t["act_btn_go"],
        default_accept=True,
        border_color=C.CYAN,
    )
    if not go:
        return

    clear_screen()
    print_banner(lang)
    code, _ = run_ultra0_translated(plan_args, lang)
    print()

    # Ask user to confirm they accepted the offer on the MuMuPlayer screen
    accepted_offer = interactive_confirm_box(
        lang=lang,
        title=t["act_warn_title"],
        lines=[t["act_ask_accepted"]],
        btn_cancel=t["act_no"],
        btn_accept=t["act_yes"],
        default_accept=(code == 0),
        border_color=C.GREEN if code == 0 else C.YELLOW,
    )
    if accepted_offer:
        state[state_key] = True
        save_state(state)
        print(f"\n{C.BG_GREEN}{C.WHITE}{C.BOLD}  {t['step_completed_ok']}  {C.RESET}")
    else:
        print(f"\n{C.YELLOW}{C.BOLD}  {t['step_not_completed']}{C.RESET}")
    input(t["press_enter"])


def run_list_offers(state: dict):
    """Replaces and unifies `1_ver_lista_ofertas.bat` (`--list --plan pro12`)."""
    lang = state["lang"]
    t = T[lang]
    clear_screen()
    print_banner(lang)
    run_ultra0_translated(["--account", "current@device", "--no-add", "--force", "--list", "--plan", "pro12"], lang)
    input(t["press_enter"])


def show_help(state: dict):
    """Replaces and unifies `instrucoes_de_uso.txt` with rich ANSI color highlights."""
    lang = state["lang"]
    t = T[lang]
    clear_screen()
    print_banner(lang)
    render_colored_help(t["help_content"])
    input(t["press_enter"])


# ───────────────────────── Main Menu Loop ─────────────────────────
def format_menu_item(label: str, done: bool, unlocked: bool, lang: str) -> str:
    t = T[lang]
    if done:
        badge = f"{C.BG_GREEN}{C.WHITE}{C.BOLD} ✓ {t['status_ready']} {C.RESET}"
        return f"  {C.GREEN}{C.BOLD}{label:<58}{C.RESET} {badge}"
    if not unlocked:
        badge = f"{C.DIM}[🔒 {t['status_locked']}]{C.RESET}"
        return f"  {C.DIM}{label:<58}{C.RESET} {badge}"
    badge = f"{C.YELLOW}[• {t['status_pending']}]{C.RESET}"
    return f"  {C.WHITE}{C.BOLD}{label:<58}{C.RESET} {badge}"


def main():
    state = load_state()
    # Always prompt language choice before loading the main menu
    state["lang"] = select_language(state.get("lang"))
    save_state(state)

    while True:
        lang = state["lang"]
        t = T[lang]
        clear_screen()
        print_banner(lang)

        print(f"  {C.CYAN}{C.BOLD}━━━ {t['menu_header']} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}\n")

        print(format_menu_item(t["opt1"], state["step1_installed"], True, lang))
        print(format_menu_item(t["opt2"], state["step2_prepared"], True, lang))
        print(format_menu_item(t["opt3"], state["step3_done"], state["step2_prepared"], lang))
        print(format_menu_item(t["opt4"], state["step4_done"], state["step3_done"], lang))
        print(format_menu_item(t["opt5"], state["step5_done"], state["step4_done"], lang))
        print(format_menu_item(t["opt6"], state["step6_done"], True, lang))
        print()
        print(f"  {C.CYAN}{C.BOLD}{t['opt7']}{C.RESET}")
        print(f"  {C.BLUE}{t['opt_list']}{C.RESET}")
        print(f"  {C.MAGENTA}{t['opt_lang']}{C.RESET}")
        print(f"  {C.RED}{t['opt8']}{C.RESET}")
        print(f"\n  {C.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")

        choice = input(f"\n  {C.BOLD}{t['prompt_choice']}{C.RESET}").strip().upper()

        if choice == "1":
            run_step1_install_env(state)
        elif choice == "2":
            run_step2_prepare_env(state)
        elif choice == "3":
            run_activation_step(
                state,
                step_num=3,
                plan_args=["--account", "current@device", "--no-add", "--force", "--plan", "pro12"],
                state_key="step3_done",
            )
        elif choice == "4":
            run_activation_step(
                state,
                step_num=4,
                plan_args=["--account", "current@device", "--no-add", "--force", "--stack", "--plan", "pro6"],
                state_key="step4_done",
            )
        elif choice == "5":
            run_activation_step(
                state,
                step_num=5,
                plan_args=["--account", "current@device", "--no-add", "--force", "--stack", "--plan", "pro6b"],
                state_key="step5_done",
            )
        elif choice == "6":
            run_activation_step(
                state,
                step_num=6,
                plan_args=["--account", "current@device", "--no-add", "--force", "--stack", "--plan", "pro6c"],
                state_key="step6_done",
            )
        elif choice == "7":
            show_help(state)
        elif choice == "O":
            run_list_offers(state)
        elif choice == "L":
            state["lang"] = select_language(state.get("lang"))
            save_state(state)
        elif choice in ("8", "Q", "EXIT", "SAIR"):
            clear_screen()
            sys.exit(0)
        else:
            print(f"\n  {C.RED}{t['invalid_choice']}{C.RESET}")
            input(t["press_enter"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.RESET}")
        sys.exit(0)
