import React, { useEffect, useRef, useState } from 'react';
import {
  ChevronLeft, Menu, Plus, Send, Share2, FileText,
  MapPin, Clock, Receipt, X,
} from 'lucide-react';

const MAX = 4;
const uid = () => Math.random().toString(36).slice(2, 10);
const now = () => {
  const d = new Date();
  const h = d.getHours();
  const m = String(d.getMinutes()).padStart(2, '0');
  const ampm = h < 12 ? '오전' : '오후';
  return `${ampm} ${((h + 11) % 12) + 1}:${m}`;
};

const statusTime = () => {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

const C = {
  olive: '#b3c476',
  oliveDark: '#5a6141',
  oliveSoft: '#e5edbf',
  ink: '#515940',
  muted: '#747b5d',
  orange: '#ffa42b',
  bg: '#fdfdfb',
  line: '#e6e6dd',
  myBubble: '#d9e4bf',
  otherBubble: '#f4f7ec',
};

export default function ChatRoom({ onBack }) {
  const [time, setTime] = useState(statusTime);
  const [participants, setParticipants] = useState(['나']);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [proposalOpen, setProposalOpen] = useState(false);
  const [proposalPrice, setProposalPrice] = useState(8000);
  const [confirmed, setConfirmed] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    const timer = window.setInterval(() => setTime(statusTime()), 30000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const addJoin = (name) => {
    if (confirmed || participants.includes(name)) return;
    const next = [...participants, name];
    setParticipants(next);
    const left = Math.max(MAX - next.length, 0);
    const t = now();
    setMessages((m) => [
      ...m,
      { id: uid(), kind: 'system', text: `${name}가 참여했어요`, time: t },
      ...(left > 0
        ? [{ id: uid(), kind: 'system', text: `${left}명만 더 모이면 주문이 가능해요!`, time: t }]
        : []),
    ]);
  };

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages((m) => [...m, { id: uid(), kind: 'me', text: input.trim(), time: now() }]);
    setInput('');
  };

  const shareLink = async () => {
    const url = typeof window !== 'undefined' ? window.location.href : '';
    try {
      if (navigator.share) await navigator.share({ title: '양배추 같이 사요', url });
      else { await navigator.clipboard.writeText(url); alert('초대 링크가 복사되었어요!'); }
    } catch {}
    const pool = ['민지', '수현', '지훈', '예린', '도윤'];
    const next = pool.find((n) => !participants.includes(n));
    if (next) addJoin(next);
  };

  const sendProposal = () => {
    setMessages((m) => [...m, {
      id: uid(), kind: 'proposal', time: now(),
      pricePerPerson: Math.round(proposalPrice / participants.length),
      totalPrice: proposalPrice, headcount: participants.length,
    }]);
    setProposalOpen(false); setMenuOpen(false);
  };

  const confirmProposal = (pid) => {
    if (confirmed) return;
    const p = messages.find((m) => m.id === pid);
    const total = p?.totalPrice ?? 0;
    const headcount = participants.length;
    setConfirmed(true);
    setMessages((m) => [
      ...m.map((x) => (x.id === pid ? { ...x, confirmed: true } : x)),
      { id: uid(), kind: 'confirmed-notice', time: now(), by: '나', headcount },
      { id: uid(), kind: 'summary', time: now(),
        pricePerPerson: Math.round(total / headcount),
        location: '태평1동 구매', deadline: '오늘 18:30' },
    ]);
  };

  return (
    <div style={S.stage}>
      <div style={S.frame}>
        {/* status bar */}
        <div style={S.statusBar}><span>{time}</span><span /></div>

        {/* header */}
        <div style={S.header}>
          <button style={S.iconBtn} onClick={onBack} aria-label="뒤로"><ChevronLeft size={20} /></button>
          <div style={S.title}>양배추 같이 사요</div>
          <button style={S.iconBtn} onClick={() => setMenuOpen(true)} aria-label="메뉴"><Menu size={20} /></button>
        </div>

        {/* status row */}
        <div style={S.statusRow}>
          <span style={{ color: C.oliveDark, fontWeight: 600 }}>{participants.length}/{MAX}명 참여중</span>
          <span style={{ color: C.muted, fontSize: 12 }}>마감까지 30분</span>
        </div>

        {/* messages */}
        <div ref={scrollRef} style={S.messages}>
          {messages.length === 0 && (
            <p style={{ textAlign: 'center', color: C.muted, fontSize: 12 }}>
              우측 상단 메뉴 → 링크 공유로 참여자를 추가해보세요.
            </p>
          )}
          {messages.map((m) => (
            <Bubble key={m.id} msg={m} onConfirm={confirmProposal} confirmed={confirmed} />
          ))}
        </div>

        {/* input */}
        <div style={S.inputBar}>
          <button style={S.roundBtn}><Plus size={16} /></button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="메시지를 입력하세요"
            style={S.input}
          />
          <button onClick={sendMessage} style={{ ...S.roundBtn, color: C.olive, border: 'none' }}>
            <Send size={16} />
          </button>
        </div>

        {/* drawer */}
        {menuOpen && (
          <>
            <div style={S.backdrop} onClick={() => setMenuOpen(false)} />
            <div style={S.drawer}>
              <div style={S.drawerHeader}>
                <div style={{ fontWeight: 700 }}>채팅방 메뉴</div>
                <button style={S.iconBtn} onClick={() => setMenuOpen(false)}><X size={18} /></button>
              </div>

              <button
                style={{ ...S.menuBtn, opacity: confirmed ? 0.5 : 1 }}
                disabled={confirmed}
                onClick={() => setProposalOpen(true)}
              >
                <FileText size={16} /> 공동구매 확정 보내기
              </button>

              <div style={S.participantsBox}>
                <div style={{ fontWeight: 600, marginBottom: 6 }}>참여자 ({participants.length}/{MAX})</div>
                {participants.map((p) => <div key={p} style={{ color: C.muted, fontSize: 13 }}>· {p}</div>)}
              </div>

              <button
                style={{ ...S.menuBtn, background: C.oliveSoft, borderColor: C.olive,
                  opacity: confirmed || participants.length >= MAX ? 0.5 : 1 }}
                disabled={confirmed || participants.length >= MAX}
                onClick={shareLink}
              >
                <Share2 size={16} /> 링크 공유하기
              </button>

              {proposalOpen && (
                <div style={S.proposalBox}>
                  <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8 }}>공동구매 확정 메시지</div>
                  <label style={{ fontSize: 12, color: C.muted }}>총 금액 (원)</label>
                  <input
                    type="number"
                    value={proposalPrice}
                    onChange={(e) => setProposalPrice(Number(e.target.value) || 0)}
                    style={S.priceInput}
                  />
                  <div style={{ fontSize: 12, color: C.muted, marginBottom: 10 }}>
                    {participants.length}명 기준 1인당 약{' '}
                    <b style={{ color: C.ink }}>
                      {participants.length ? Math.round(proposalPrice / participants.length).toLocaleString() : 0}원
                    </b>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button style={S.cancelBtn} onClick={() => setProposalOpen(false)}>취소</button>
                    <button style={S.primaryBtn} onClick={sendProposal}>채팅방에 보내기</button>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Bubble({ msg, onConfirm, confirmed }) {
  if (msg.kind === 'system') return (
    <div style={{ display: 'flex', justifyContent: 'center', gap: 6, alignItems: 'center' }}>
      <span style={{ background: C.oliveSoft, color: C.oliveDark, padding: '6px 12px',
        borderRadius: 999, fontSize: 12, fontWeight: 500 }}>{msg.text}</span>
      <span style={{ fontSize: 10, color: C.muted }}>{msg.time}</span>
    </div>
  );

  if (msg.kind === 'me') return (
    <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'flex-end', gap: 6 }}>
      <span style={{ fontSize: 10, color: C.muted }}>{msg.time}</span>
      <div style={{ maxWidth: '70%', background: C.myBubble, padding: '8px 12px',
        borderRadius: '16px 16px 4px 16px', fontSize: 14 }}>{msg.text}</div>
    </div>
  );

  if (msg.kind === 'proposal') return (
    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
      <div style={{ width: '85%', background: '#fff', border: `1px solid ${C.line}`,
        borderRadius: 16, padding: 14, boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8 }}>
          {msg.headcount}명으로 공동구매 확정할까요?
        </div>
        <p style={{ fontSize: 12, color: C.muted, margin: '0 0 10px' }}>
          현재 인원으로 1/N 금액을 확정합니다.
        </p>
        <div style={{ background: C.oliveSoft, borderRadius: 8, padding: 10, fontSize: 12, marginBottom: 10 }}>
          <Row label="총 금액" value={`${msg.totalPrice.toLocaleString()}원`} />
          <Row label="1/N 금액" value={`${msg.pricePerPerson.toLocaleString()}원`} valueColor={C.oliveDark} />
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <button style={S.outlineBtn}>더 기다릴게요</button>
          <button
            disabled={confirmed || msg.confirmed}
            onClick={() => onConfirm(msg.id)}
            style={{ ...S.primaryBtn, opacity: msg.confirmed ? 0.5 : 1 }}
          >
            {msg.confirmed ? '확정됨' : '공동구매 확정하기'}
          </button>
        </div>
        <div style={{ textAlign: 'right', fontSize: 10, color: C.muted, marginTop: 6 }}>{msg.time}</div>
      </div>
    </div>
  );

  if (msg.kind === 'confirmed-notice') return (
    <div style={{ display: 'flex', justifyContent: 'center' }}>
      <span style={{ background: C.orange, color: '#fff', padding: '8px 14px',
        borderRadius: 999, fontSize: 12, fontWeight: 600 }}>
        {msg.by}님이 {msg.headcount}명으로 공동구매 확정했어요
      </span>
    </div>
  );

  if (msg.kind === 'summary') return (
    <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
      <div style={{ width: '85%', background: C.oliveSoft, border: `1px solid ${C.olive}`,
        borderRadius: 16, padding: 14 }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 10 }}>확정 내용을 확인해주세요!</div>
        <IconRow icon={<Receipt size={14} color={C.oliveDark} />} label="1/N 금액" value={`${msg.pricePerPerson.toLocaleString()}원`} />
        <IconRow icon={<MapPin size={14} color={C.oliveDark} />} label="거래장소" value={msg.location} />
        <IconRow icon={<Clock size={14} color={C.oliveDark} />} label="모임마감시간" value={msg.deadline} />
        <div style={{ textAlign: 'right', fontSize: 10, color: C.muted, marginTop: 6 }}>{msg.time}</div>
      </div>
    </div>
  );

  return null;
}

const Row = ({ label, value, valueColor }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 2 }}>
    <span style={{ color: C.muted }}>{label}</span>
    <span style={{ fontWeight: 700, color: valueColor || C.ink }}>{value}</span>
  </div>
);

const IconRow = ({ icon, label, value }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, marginBottom: 6 }}>
    {icon}
    <span style={{ flex: 1, color: C.muted }}>{label}</span>
    <span style={{ fontWeight: 700 }}>{value}</span>
  </div>
);

const S = {
  stage: { minHeight: '100vh', display: 'grid', justifyContent: 'center', alignContent: 'start', background: '#fff' },
  frame: { position: 'relative', width: 310, minHeight: 665, background: C.bg, overflow: 'hidden', display: 'flex', flexDirection: 'column' },
  statusBar: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: 36, padding: '12px 20px 0', fontSize: 13, fontWeight: 700, color: '#1e2528' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', borderBottom: `1px solid ${C.line}` },
  title: { fontWeight: 700, fontSize: 15 },
  iconBtn: { background: 'transparent', border: 'none', padding: 6, color: C.ink, display: 'flex' },
  statusRow: { margin: '10px 12px 0', padding: '8px 12px', border: `1px solid ${C.olive}66`, background: C.oliveSoft, borderRadius: 8, display: 'flex', justifyContent: 'space-between', fontSize: 13 },
  messages: { flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: 10 },
  inputBar: { display: 'flex', alignItems: 'center', gap: 6, padding: '8px 10px', borderTop: `1px solid ${C.line}`, background: '#fff' },
  roundBtn: { width: 32, height: 32, borderRadius: 999, border: `1px solid ${C.line}`, background: '#fff', color: C.muted, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  input: { flex: 1, border: `1px solid ${C.line}`, background: '#f7f7f1', borderRadius: 999, padding: '8px 14px', fontSize: 14, outline: 'none' },
  backdrop: { position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.3)', zIndex: 10 },
  drawer: { position: 'absolute', top: 0, right: 0, bottom: 0, width: 240, background: '#fff', padding: 16, zIndex: 11, display: 'flex', flexDirection: 'column', gap: 10, boxShadow: '-4px 0 12px rgba(0,0,0,0.1)' },
  drawerHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  menuBtn: { display: 'flex', alignItems: 'center', gap: 8, padding: '10px 12px', border: `1px solid ${C.line}`, background: '#fff', borderRadius: 8, fontSize: 13, textAlign: 'left', width: '100%' },
  participantsBox: { border: `1px solid ${C.line}`, borderRadius: 8, padding: 10, fontSize: 13 },
  proposalBox: { marginTop: 10, padding: 12, border: `1px solid ${C.line}`, borderRadius: 12, background: '#fafaf5' },
  priceInput: { width: '100%', marginTop: 4, marginBottom: 8, padding: '6px 10px', border: `1px solid ${C.line}`, borderRadius: 6, fontSize: 13 },
  cancelBtn: { flex: 1, padding: '8px', border: `1px solid ${C.line}`, background: '#fff', borderRadius: 8, fontSize: 12 },
  primaryBtn: { flex: 1, padding: '8px', border: 'none', background: C.olive, color: '#fff', borderRadius: 8, fontSize: 12, fontWeight: 600 },
  outlineBtn: { flex: 1, padding: '8px', border: `1px solid ${C.line}`, background: '#fff', borderRadius: 8, fontSize: 12 },
};
