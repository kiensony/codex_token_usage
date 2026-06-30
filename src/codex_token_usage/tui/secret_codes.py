from __future__ import annotations

import base64
import curses
import shutil
import socket
import sys
import zlib
from typing import Protocol, TextIO

from ..theme import ThemeConfig, theme_palette

SECRET_CODE_KEY = 19
SECRET_PROMPT = "???: "
SECRET_DISMISS_KEYS = (27, ord("q"), ord("Q"))

EFFECT_BIRTHDAY = "birthday_cake"
EFFECT_HEART = "heart"
EFFECT_NYAN = "nyan"
EFFECT_TRANS_FLAG = "trans_flag"
EFFECT_EMERGENCY = "emergency"
EFFECT_PWNED = "pwned"

EMERGENCY_MESSAGE = "WE ARE NOT ALLOW TO CALL EMERGENCY HERE"
EMERGENCY_EXIT_CODE = 1
EMERGENCY_CRASH_LINES = (
    "///// SYSTEM SIGNAL LOST /////",
    "W E  ARE N0T  ALL0W  TO  CALL  EMERGENCY  HERE",
    "WE ARE NOT /ALLOW/ TO CALL EMERGENCY HERE",
    "W# ARE N*T ALL@W TO C#LL EMERGENCY H#RE",
    "///// TERMINAL STATE SHATTERED /////",
)
EMERGENCY_CODES = frozenset(("113", "110", "112", "911"))
SECRET_CODE_EFFECTS = {
    "2109": EFFECT_BIRTHDAY,
    "1976": EFFECT_HEART,
    "2011": EFFECT_NYAN,
    "iamdeveloper": EFFECT_TRANS_FLAG,
    "pwned": EFFECT_PWNED,
    **{code: EFFECT_EMERGENCY for code in EMERGENCY_CODES},
}
NYAN_FRAME_PAYLOAD = """
c-rlq%aW|B5{Bm$=OLIeAqdCt2o<Lt?wZ34BAD{{J2OEAwW_c#x^^$=wQNhP{pBLcXJ#Vht10x(8RMM
uul)5zzLjo2um0tm!rmVw{Cc|ZqlD!td<t*A!lF2)RdeyjU&owtQ6-K^(vEuHv{6n4#c`EBZYsQsh6C
#2;Avfti8g84EV=J)x7&3+!JeSl24P4l<YeI|1YM?aUkFT+YL}CXJuD+FA)$27nw2jRldDp!(zF?bQP
sMn)Ptf6Q0~h1T~E?mgz1=Fm8!Go$IX2fE|XwznovZFjse0_2N!*V{AH-0BF*Y9D&=W&ElfqM85K$})
b@n-0n5ubWc>28B2^|Qwf9Csmh33p=S8$y<_gJeB!6fr>Sf{91s}OK(bBat2=_6`JINGgu)likQgeXy
pkeKK^S-#1RJXQ(my#J8my1(VkW5nsm1HC=w8M2+(+$G-7uKdL2^MxJuOYz}Mb|SY;oeQ9jXCc79+Va
8`w-wPO@K`eIZl=1{cy2PYXOhsaRdGH28E%lUAlZ>VT3Zh>oMy}DOzwmmuN(Ta5`w2P$&2-J?!!v>i7
qhW6=n#5(*!1iykLL-q3g23m#O}sXB|aNegKVTqN!~zmjbz`|{@0U+B2?O`<*xs9nt&hnm-dF$Uc@ug
ei~356lC?`Y{cBoriM<3jhM*&Ve?v}x!OmOVqgr9~KuluLEg{kS_yIGj(Jr|_fBr_%=rLpKZee^~OJh
3$~U{zcvYqmHR#t=<{_{BOgc2p%~-JYz`#H^Ti<#Ot`_P2t=1AYma668`Vwrc?O!q~amMf<_~U<k-aj
MjfXCK=~lO06-b_V0jw*AVsyIb3y8p;7(#YiSrZ?h<2tW!k2=+^uz?lVJi*jH!u(wP^b#?B=(bk%F&q
4qs3v+*3+=Dpd{B#!uKi9oB$0dqAxiO3>TsN`!2zkEy4>B(bohhrlFgkaMQ4-C+g#4^f*jTS!Pn;h8F
7c^ANq<u8>cvUTxiquts6$a4<_WPWjkMeHK#ndED?>0|x0z7VyRPxst7x$d_DnHZg=mU_xUZFYsC%e{
i3Np{NN?CE<RoiatuF;7icBgURg!8lE+_nfj1K*`kUit|%<(3}4FgOv28>sagEG5)s#ZlQ3TRbIOzP5
B#zdKjW-y)dXKq7^#mpm}C5dXq69c1NFI|CLCl^2Qos`u2WJQP;rhk<qc=r7=hHsg$C;5iSi7T2@%ko
0Hw`ALsctVH@;i+TErRkaeB4?53$;Oxr2G;1V|v#^tm&hs0rsyT?U8dua)FcSABIYHDP+}x`(aMvS1f
O8OEslEPxAs#vNSfRs1qNi>ttkA<PQpSrDN2o=t|q4xffS`wYynsFk5#`xAj+PX=-dKj8r45Mj8{2QQ
8gHqILHHx>2gQb~PyKRztQ`1Mx(=Zue|JxKUdSm$IQ?+Xilj4=O+2MK$%yRd-ajO5Ns<6PJ^$DFKCH2
&th7q$4O|4dOM)0vz4$aM&mwi_ig3X<j1IDf&`r!w=YY<(&-pfB0_*l}3+z}DxwV(Zg=+}6iExAh?&V
GpqN={mBuQO0IlAC}vG6MT7S>r-rAvGwUXDILD+69zNwKv=*@xCR51+Y?)#X<xUn^~u7BKdk4}?1e?_
(_;DZ%+{wLEpOCh>yv92vK{zn<};e>z>jIG<CWGmvLHMvHE+pg)CcjYU;*1;ch$<}#t7>gU&XO!!lSK
Eww#+$Adj~NxW<%GCFkk~L$ZKpr{EgL16iq@!Sx2=67D41o?$~;G0<9&fv`mODq9~Cc5o6dDg&iN)X8
g$42nM&o}2oZq?!NwVc?+2$mlk+^)W(`nGs{qwrC;YT>9|zWqPBn582)@#+SA}P#0)ZRi3+TdGC3lBW
J_QY?HaL^~s6Js3<3B@G~JamYz)ozERGox9OckldVrucw*KA=d<#?lL(x`f0!_j{-7Kyy}K|zKM&Z~>
?thlI8?D=|DyidF#U<J_;Ftn&eTWrX79`CL=mU(fx=uIAq>x$Ho{<>?=2iCyF7?}g(sluBi~b)i}XsC
>yP)@Pl}pbf$!$H{YFvqC)CG;n))QZGcNMyZ%`k7QlFFhl+=d_6MqHuvBvC7edzp0)438ve3|;hpt<+
P!>)vz_M$$D39_1#J5wJRy>KXHVorNgADw-#zCwM<u6mvNXvv`V$(4%_WCu?XmJ&0XiWUo}t@CQ9J}b
-zPSJEOn>?}A?|qF3@av23-QGqKd;7wi)aL`j-{1~Ug+&y|d35Bv3KwsNjo($+j<-=C_AY9UoJU)}cj
JP4>9u>kSJ*;*;NkR;vH8V{gRbL~f&7)if*&I+qW^n}TDzgQ<}vIk%%|%8c12&-NY5V7{4&Cv;W3&EZ
)PEW<cNFZKz)WlK5tMTohgqPe7VFj)KA(fx%nXVnaA-dJiO)v=(E&kpgeBPzpM8CTBSa4o-U7<w^5&G
9$s#No2qCa*c`NRY3!PW+pOCzPtnU*lHGb-9~Z6By6Y45k>0ik6nYd+$k_xjb(!Od`UsX>l``(s!D5{
?xt2Zh@WLQMOhXo|KyQ}?^|3*7`sQGrlbcJcYngMaZHj)IJZk4Wwd$!AQ(T`MP{@dZ`Se#W;7?!k@S+
s5+h>lBq_W9PMSU=!5XQI>i1#8n`r|tU*F^S0W18an^!?;orZJ!pmJ8Ob!cx{Dc1^Bj=;1XJn1%SsyO
T3rMSX(N!li&hf(x0LkAeznxS$puUTO^iK}Ac(R^s|N3pdc3`2^e8SI;R=P3!YE#-Y~Xn>@w!5pXUeY
rz*KDXxzYY}0MA!NZHC{>TVP;e~`UlgY6VVlXt~?4A4ZGum>CUwRODCj6Oa!4tmhDs1CH!hLsyaNy{{
$=`_3^Ewd-0V6%^OeC<VqdTaMUk_0H4)xhv&^j0xhMpgD9V>rO2h#uWV+Q8%xN=5w{tGzQF7E->gyXh
wJRdCTqjLO?Dtk+qK+nR~M~)UhrK6PykHY#yy&)HugnI79@<{=I^4KEB^{L^@IK18pU$Q-qErx9s1Tx
dUMO>e*6b9w%XKa0DramKz==+tpK9u{9+WO?UK4D?&Lw}@mTpyqE+;52M^UT)AW|IKbb*piGD58!}QJ
9p{K1FkG!%Yu?6Fze<;`(I32JKjeWF-^ExIP=BImb8!*_qk;=oHsS%;WmFn1=rp*Jo@Poi$scIcLVR1
VGftFs_eSjq8KaoGGpk2`feG8>2asnGYHJEGSS2Xz;NX*GHpujf34T#r1(zzbTq?7=tJWzl`jYqdKRk
>;-($Q(PZ!w#M~IUR)LF>74hIu@SK!_=osK&v|w9dKt~R4Wb&Q=A<W`h^jD<U<Qqm=5c)_XD{9<>S)d
eI)hAsqAe*9v}`@b^_h8brO(+2s2RW1wmzJ)L^ma+KM~Pq+gli;_jnLE?Dfw{eNN%uCT#vX;Xfm;&qu
I|Ym63h8larQzd(5AD7KF<K2il33>A)II|(Px-qKNQ7vbq`%j77wi!c}2>Re4;GCLKu)zaHKdgK_*c_
ck^0+j4S^CNcQ{xyCoSMDcmX7HtO=o+Ir>(c8hW1%KnpAFaXBARnOTAbPXRC9RQSs3Z-&Ak}S*)>IT9
*3#fJ_5$iWcG6HuI?RMpKgn-Pj}58UU9RB*H5FH71Fa(xSu?{T=MYhhPXa$DB{`FVQa2sa}O_aF3TQX
foiOUflPB_bq~C~Fi!Mh4lnfZ5;|GiOjcoJsngQ9hS<%MX;J0hHS_RV#PxCH;U(124#~qSK6kXbZ|g%
Lo#CS*4=<ZNygnV*=WbHSvO?+M)z3V<FpzXq#%=WQ@<YVtDO_}gfDFfei|c^XRpBMD;^F1U!;6!L7jO
0OdJ@eU_R%zLxSdJ#@S0isL@yEVnav(vdS%Y80@hF4(ZkDT2dg@oGh^}v4=>pk&3PWEdSx=NyL-;@@h
SXEgsnY5SXgot6OUe(enWT)1N6XA><hwt>M|cVihZZ3qaa7Iy^ESg05|~^|33BM^zd-Vz+8lFM>-kED
f}J?;KvB-M?m$r6}581gEa<!-ck6utJpV-x`<o1COo(G86!1Ixfab?wo@PeXgY+;%+9Btwq2J~dg+F^
J{ua>EOyV9xIT8~;kAwWY@fNkrapy-*Soep{T+ud_rSxe-|pe{bmn&0i$C+YK8gAWMxk}I9?#8N=R)J
;VUK`Q^6(N5JiI8X&*b5S71bpCIIfQ)4=)$tn5BnTS9o}pz$dS?dw9)e@tWrFileOtS9(r;vWJ&T9$v
BZ@M^d989ch|GOiCn5uM>nMSbQTUi>8wFTb3+%a1d;dw<8nD^4C>f#!|ZA+{SC&8O|6G@H5IkUiIJ?%
}1WR<ef|#|0EZlZV&3SC^VmAU%0_Rn+GV53g*`qwmh#o&!1KRL6W}=JvwFYn!7L-!yZ34S1Feh#ma|a
x#!p_=Cd2sbhro&F?O(p&y5Vxt7Ye&l&R(VYsKkLo~iHZMVAnTv2a~j{GrU^Z#uVQvD0@T@+O
"""
NYAN_COLORS = (
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 0, 255),
    (0, 255, 255),
    (255, 255, 255),
)
NYAN_MAX_WIDTH = 320
PWNED_BOOT_LINES = (
    "[*] initialising ceremonial intrusion apparatus",
    "[*] consulting the peer-reviewed packet grimoire",
    "[*] negotiating imaginary privilege escalation",
    "[*] dusting fingerprints from /var/log/melodrama",
    "[+] success: pretend root shell established",
)
PWNED_TROLL_MESSAGES = (
    "Quite so. Your submission has been carefully examined, and you have been trolled.",
    "A rigorous assessment reveals no shell here; you have been trolled with modest elegance.",
    "The committee finds, beyond reasonable doubt, that you have been trolled.",
    "Your command is academically fascinating, but operationally fictional. Consider yourself trolled.",
    "With due scholarly restraint: this is terminal pantomime, and you have been trolled.",
)


class EmergencyCrash(SystemExit):
    def __init__(self) -> None:
        super().__init__(EMERGENCY_EXIT_CODE)


class SecretCodeRenderer(Protocol):
    stdscr: object

    def safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        ...

    def render_themed_text(
        self,
        y: int,
        x: int,
        text: str,
        base_attr: int = 0,
        start_index: int = 0,
    ) -> None:
        ...

    def preview_attr(self, rgb: tuple[int, int, int], base_attr: int = 0) -> int:
        ...


def secret_effect_for_code(code: str) -> str | None:
    return SECRET_CODE_EFFECTS.get(code.strip())


def render_secret_code(ui: SecretCodeRenderer, code: str) -> bool:
    effect = secret_effect_for_code(code)
    if effect is None:
        return False
    render_secret_effect(ui, effect)
    return True


def render_secret_effect(ui: SecretCodeRenderer, effect: str) -> None:
    if effect == EFFECT_BIRTHDAY:
        render_birthday_cake(ui)
    elif effect == EFFECT_HEART:
        render_heart(ui)
    elif effect == EFFECT_NYAN:
        render_nyan(ui)
    elif effect == EFFECT_TRANS_FLAG:
        render_trans_flag(ui)
    elif effect == EFFECT_EMERGENCY:
        render_emergency(ui)
    elif effect == EFFECT_PWNED:
        render_pwned(ui)


def render_birthday_cake(ui: SecretCodeRenderer) -> None:
    frames = (
        (
            "          ,   ,   ,",
            "         ||  ||  ||",
            "      ___||__||__||___",
            "     |^^^^^^^^^^^^^^^^^|",
            "     |    HAPPY 5TH    |",
            "     |_________________|",
            "    |~~~~~~~~~~~~~~~~~~~|",
            "    |    BIRTHDAY!!!    |",
            "    |___________________|",
        ),
        (
            "          .   .   .",
            "         ||  ||  ||",
            "      ___||__||__||___",
            "     |~~~~~~~~~~~~~~~~~|",
            "     |    HAPPY 5TH    |",
            "     |_________________|",
            "    |^^^^^^^^^^^^^^^^^^^|",
            "    |    BIRTHDAY!!!    |",
            "    |___________________|",
        ),
        (
            "          *   *   *",
            "         ||  ||  ||",
            "      ___||__||__||___",
            "     |*****************|",
            "     |    HAPPY 5TH    |",
            "     |_________________|",
            "    |~~~~~~~~~~~~~~~~~~~|",
            "    |    BIRTHDAY!!!    |",
            "    |___________________|",
        ),
    )
    _animate_frames_until_dismissal(ui, frames, themed=True, frame_ms=90)


def render_heart(ui: SecretCodeRenderer) -> None:
    frames = (
        (
            "  **   **  ",
            " ********* ",
            " ********* ",
            "  *******  ",
            "   *****   ",
            "    ***    ",
            "     *     ",
        ),
        (
            " ***   *** ",
            "***********",
            "***********",
            " ********* ",
            "  *******  ",
            "    ***    ",
            "     *     ",
        ),
        (
            "  **   **  ",
            " ********* ",
            "  *******  ",
            "   *****   ",
            "    ***    ",
            "     *     ",
        ),
    )
    _animate_frames(ui, frames, attr=curses.A_BOLD)
    _wait_for_secret_dismissal(ui)


def render_nyan(ui: SecretCodeRenderer) -> None:
    stdscr = getattr(ui, "stdscr", None)
    if stdscr is None:
        return
    frames = _nyan_frames()
    frame_ms = 100
    if hasattr(stdscr, "timeout"):
        stdscr.timeout(frame_ms)
    try:
        frame_index = 0
        while True:
            stdscr.erase()
            height, width = stdscr.getmaxyx()
            frame = frames[frame_index % len(frames)]
            attr = _preview_or_base_attr(
                ui,
                NYAN_COLORS[frame_index % len(NYAN_COLORS)],
                curses.A_BOLD,
            )
            _draw_nyan_frame(ui, frame, width, height, attr)
            stdscr.refresh()
            key = stdscr.getch()
            if key in SECRET_DISMISS_KEYS:
                return
            frame_index += 1
    finally:
        if hasattr(stdscr, "timeout"):
            stdscr.timeout(-1)


def _nyan_frames() -> tuple[tuple[str, ...], ...]:
    encoded = "".join(NYAN_FRAME_PAYLOAD.split()).encode("ascii")
    text = zlib.decompress(base64.b85decode(encoded)).decode("utf-8")
    return tuple(tuple(frame.splitlines()) for frame in text.split("\f"))


def _draw_nyan_frame(
    ui: SecretCodeRenderer,
    frame: tuple[str, ...],
    width: int,
    height: int,
    attr: int,
) -> None:
    if width <= 0 or height <= 0:
        return
    resized = _resize_nyan_frame(frame, width)
    frame_height = len(resized)
    frame_width = max((len(row) for row in resized), default=0)
    if not resized or frame_height == 0 or frame_width == 0:
        return
    top = max(0, (height - frame_height) // 2)
    left = max(0, (width - frame_width) // 2)
    row_offset = max(0, (frame_height - height) // 2)
    column_offset = max(0, (frame_width - width) // 2)
    visible_height = min(height, frame_height)
    visible_width = min(width, frame_width)
    for row in range(visible_height):
        line = resized[row + row_offset][
            column_offset : column_offset + visible_width
        ]
        ui.safe_addstr(top + row, left, line, attr)


def _resize_nyan_frame(frame: tuple[str, ...], screen_width: int) -> tuple[str, ...]:
    source_height = len(frame)
    source_width = max((len(row) for row in frame), default=0)
    if source_height == 0 or source_width == 0 or screen_width <= 0:
        return ()
    target_width = min(screen_width, NYAN_MAX_WIDTH)
    target_height = max(1, round(source_height * target_width / source_width))
    padded = tuple(row.ljust(source_width) for row in frame)
    if target_width == source_width and target_height == source_height:
        return padded
    rows: list[str] = []
    for target_y in range(target_height):
        source_y = min(source_height - 1, target_y * source_height // target_height)
        source_row = padded[source_y]
        rows.append(
            "".join(
                source_row[
                    min(source_width - 1, target_x * source_width // target_width)
                ]
                for target_x in range(target_width)
            )
        )
    return tuple(rows)


def render_trans_flag(ui: SecretCodeRenderer) -> None:
    stdscr = getattr(ui, "stdscr", None)
    if stdscr is None:
        return
    palette = theme_palette(ThemeConfig(enabled=True, preset="trans"))
    if not palette:
        return
    wave_offsets = (0, 1)
    frame_ms = 140
    if hasattr(stdscr, "timeout"):
        stdscr.timeout(frame_ms)
    try:
        frame = 0
        while True:
            stdscr.erase()
            height, width = stdscr.getmaxyx()
            available_width = max(1, width - 8)
            segment_width = max(1, available_width // 12)
            cycle_width = segment_width * len(wave_offsets)
            if available_width >= cycle_width:
                flag_width = available_width - (available_width % cycle_width)
            else:
                flag_width = available_width
            stripe_height = max(
                1,
                min(
                    max(1, flag_width // 36),
                    max(1, (height - 4) // (len(palette) + 2)),
                ),
            )
            wave_height = (
                len(palette) * stripe_height
                + max(wave_offsets)
                - min(wave_offsets)
            )
            top = max(0, (height - wave_height) // 2 - min(wave_offsets))
            left = max(0, (width - flag_width) // 2)
            for column in range(0, flag_width, segment_width):
                offset = wave_offsets[
                    (frame + column // segment_width) % len(wave_offsets)
                ]
                for row, rgb in enumerate(palette):
                    attr = _preview_or_base_attr(ui, rgb, curses.A_REVERSE)
                    for stripe_row in range(stripe_height):
                        ui.safe_addstr(
                            top + row * stripe_height + stripe_row + offset,
                            left + column,
                            " " * segment_width,
                            attr,
                        )
            stdscr.refresh()
            key = stdscr.getch()
            if key in SECRET_DISMISS_KEYS:
                return
            frame += 1
    finally:
        if hasattr(stdscr, "timeout"):
            stdscr.timeout(-1)


def render_pwned(ui: SecretCodeRenderer) -> None:
    stdscr = getattr(ui, "stdscr", None)
    if stdscr is None:
        return
    if hasattr(stdscr, "timeout"):
        stdscr.timeout(-1)
    hostname = _hostname()
    prompt = f"root@{hostname}:~# "
    history: list[str] = []
    boot_attr = _preview_or_base_attr(ui, (0, 255, 80), curses.A_BOLD)
    response_attr = _preview_or_base_attr(ui, (255, 235, 150), curses.A_BOLD)

    for line in PWNED_BOOT_LINES:
        history.append(line)
        _draw_pwned_terminal(ui, history, prompt, "", boot_attr)
        _napms(90)

    buffer = ""
    response_index = 0
    try:
        while True:
            _draw_pwned_terminal(ui, history, prompt, buffer, boot_attr)
            key = stdscr.getch()
            if key == 27 or (key in (ord("q"), ord("Q")) and not buffer):
                return
            if key in (10, 13, curses.KEY_ENTER):
                command = buffer.strip()
                if command:
                    history.append(f"{prompt}{buffer}")
                    history.append(PWNED_TROLL_MESSAGES[response_index])
                    response_index = (response_index + 1) % len(PWNED_TROLL_MESSAGES)
                    _draw_pwned_terminal(
                        ui,
                        history,
                        prompt,
                        "",
                        boot_attr,
                        response_attr=response_attr,
                    )
                    _napms(45)
                buffer = ""
                continue
            if key in (curses.KEY_BACKSPACE, 8, 127):
                buffer = buffer[:-1]
                continue
            if 32 <= key <= 126:
                buffer += chr(key)
    finally:
        if hasattr(stdscr, "timeout"):
            stdscr.timeout(-1)


def _draw_pwned_terminal(
    ui: SecretCodeRenderer,
    history: list[str],
    prompt: str,
    buffer: str,
    attr: int,
    response_attr: int | None = None,
) -> None:
    stdscr = getattr(ui, "stdscr", None)
    if stdscr is None:
        return
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    if height <= 0 or width <= 0:
        return
    lines = history + [f"{prompt}{buffer}"]
    top = max(0, height - len(lines) - 1)
    visible = lines[-height:]
    for row, line in enumerate(visible):
        line_attr = attr
        if response_attr is not None and line in PWNED_TROLL_MESSAGES:
            line_attr = response_attr
        ui.safe_addstr(top + row, 0, line[:width], line_attr)
    stdscr.refresh()


def _hostname() -> str:
    try:
        hostname = socket.gethostname().strip()
    except OSError:
        return "hacker"
    return hostname or "hacker"


def render_emergency(ui: SecretCodeRenderer) -> None:
    attr = _emergency_attr(ui)
    frames = (
        "WE ARE NOT ALLOW TO CALL EMERGENCY HERE",
        "W E  ARE N0T ALL0W  TO CALL EMERGENCY HERE",
        "WE ARE NOT /ALLOW/ TO CALL EMERGENCY HERE",
        "WE ARE NOT ALLOW TO CALL  EMERGENCY  HERE",
        "WE  ARE  NOT  ALLOW  TO  CALL  EMERGENCY  HERE",
    )
    for frame in frames:
        _draw_centered_lines(ui, (frame,), attr)
        _napms(25)
    _draw_centered_lines(ui, (EMERGENCY_MESSAGE,), attr)
    _wait_for_secret_dismissal(ui)
    if hasattr(ui, "suppress_farewell"):
        ui.suppress_farewell()
    raise EmergencyCrash()


def render_terminal_emergency_crash(stream: TextIO | None = None) -> None:
    output = sys.stderr if stream is None else stream
    output.write("\033[2J\033[H\033[1;31m")
    output.write(emergency_crash_screen())
    output.write("\033[0m\n")
    output.flush()


def emergency_crash_screen(
    size: tuple[int, int] | None = None,
) -> str:
    if size is None:
        terminal_size = shutil.get_terminal_size((80, 24))
        height = terminal_size.lines
        width = terminal_size.columns
    else:
        height, width = size
    top_padding = max(0, (height - len(EMERGENCY_CRASH_LINES)) // 2)
    lines = [""] * top_padding
    for line in EMERGENCY_CRASH_LINES:
        lines.append(line.center(width))
    return "\n".join(lines)


def _animate_frames(
    ui: SecretCodeRenderer,
    frames: tuple[tuple[str, ...], ...],
    attr: int = 0,
    themed: bool = False,
) -> None:
    for offset, frame in enumerate(frames * 2):
        _draw_centered_lines(ui, frame, attr, themed=themed, start_index=offset)
        _napms(35)


def _animate_frames_until_dismissal(
    ui: SecretCodeRenderer,
    frames: tuple[tuple[str, ...], ...],
    attr: int = 0,
    themed: bool = False,
    frame_ms: int = 90,
) -> None:
    stdscr = getattr(ui, "stdscr", None)
    if stdscr is None or not frames:
        return
    if hasattr(stdscr, "timeout"):
        stdscr.timeout(frame_ms)
    try:
        offset = 0
        while True:
            frame = frames[offset % len(frames)]
            _draw_centered_lines(
                ui,
                frame,
                attr,
                themed=themed,
                start_index=offset,
            )
            key = stdscr.getch()
            if key in SECRET_DISMISS_KEYS:
                return
            if key == -1:
                _napms(1)
            offset += 1
    finally:
        if hasattr(stdscr, "timeout"):
            stdscr.timeout(-1)


def _draw_centered_lines(
    ui: SecretCodeRenderer,
    lines: tuple[str, ...],
    attr: int = 0,
    themed: bool = False,
    start_index: int = 0,
) -> None:
    stdscr = getattr(ui, "stdscr", None)
    if stdscr is None:
        return
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    top = max(0, (height - len(lines)) // 2)
    for index, line in enumerate(lines):
        x = max(0, (width - len(line)) // 2)
        if themed:
            ui.render_themed_text(top + index, x, line, attr, start_index + index)
        else:
            ui.safe_addstr(top + index, x, line, attr)
    stdscr.refresh()


def _emergency_attr(ui: SecretCodeRenderer) -> int:
    try:
        return ui.preview_attr((255, 0, 0), curses.A_BOLD)
    except curses.error:
        return curses.A_BOLD


def _preview_or_base_attr(
    ui: SecretCodeRenderer,
    rgb: tuple[int, int, int],
    base_attr: int,
) -> int:
    try:
        return ui.preview_attr(rgb, base_attr)
    except curses.error:
        return base_attr


def _napms(milliseconds: int) -> None:
    try:
        curses.napms(milliseconds)
    except curses.error:
        return


def _wait_for_secret_dismissal(ui: SecretCodeRenderer) -> None:
    stdscr = getattr(ui, "stdscr", None)
    if stdscr is None:
        return
    if hasattr(stdscr, "timeout"):
        stdscr.timeout(-1)
    try:
        while True:
            key = stdscr.getch()
            if key in SECRET_DISMISS_KEYS:
                return
    finally:
        if hasattr(stdscr, "timeout"):
            stdscr.timeout(-1)
