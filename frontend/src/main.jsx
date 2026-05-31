import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ChevronLeft, MapPin, Phone, UserRound } from 'lucide-react';
import './styles.css';

const screens = ['welcome', 'phone', 'code', 'nickname', 'location', 'complete'];

function StatusBar() {
  return (
    <div className="status-bar" aria-hidden="true">
      <strong>12:00</strong>
      <div className="status-icons">
        <span className="signal"><i /><i /><i /></span>
        <span className="wifi" />
        <span className="battery"><i /></span>
      </div>
    </div>
  );
}

function NonaLogo() {
  return (
    <div className="nona-logo" aria-label="nona">
      <span>n</span>
      <span>o</span>
      <span>n</span>
      <span>a</span>
      <i />
    </div>
  );
}

function StepDots({ active }) {
  return (
    <div className="steps" aria-label={`${active + 1}단계`}>
      {[0, 1, 2].map((index) => (
        <React.Fragment key={index}>
          <span className={index === active ? 'active' : ''} />
          {index < 2 && <i />}
        </React.Fragment>
      ))}
    </div>
  );
}

function PhoneFrame({ title, children }) {
  return (
    <div className="stage">
      <div className="frame-title">{title}</div>
      <main className="phone-frame">
        <StatusBar />
        {children}
        <div className="home-indicator" />
      </main>
    </div>
  );
}

function Header({ title, onBack, step }) {
  return (
    <>
      <button className="back-button" type="button" onClick={onBack} aria-label="뒤로가기">
        <ChevronLeft size={21} />
      </button>
      <StepDots active={step} />
      <section className="copy-block">
        <h1>{title}</h1>
      </section>
    </>
  );
}

function WelcomeIllustration() {
  return (
    <svg className="welcome-art" viewBox="0 0 300 250" role="img" aria-label="함께 장을 보는 이웃들">
      <rect x="17" y="22" width="266" height="183" rx="2" fill="#f4f4f1" />
      <rect x="31" y="47" width="238" height="142" fill="#fff" />
      <path d="M39 47h222v142H39z" fill="#f8f8f5" />
      <path d="M66 47l33 142M134 47l18 142M204 47l-24 142" stroke="#f0f0ec" strokeWidth="16" />
      <rect x="20" y="22" width="260" height="24" fill="#eeeeeb" />
      <ellipse cx="150" cy="219" rx="118" ry="10" fill="#ededec" />
      <g className="person-left">
        <path d="M62 82c14-13 28-6 27 8-2 19-30 18-33 3-1-5 1-8 6-11z" fill="#1f3037" />
        <circle cx="76" cy="95" r="16" fill="#ffad45" />
        <path d="M64 102c7 10 17 10 26 1v28H64z" fill="#ffad45" />
        <path d="M43 126c5-20 21-29 40-23 15 5 25 19 27 39l-16 51H56z" fill="#203238" />
        <path d="M36 133c10-5 21 6 27 22l21 56H61z" fill="#ffad45" />
        <path d="M96 126c12 8 16 21 16 41l-19 1z" fill="#ffad45" />
        <path d="M58 194h15l-1 34H56zM89 193h15l8 35H96z" fill="#ffad45" />
        <path d="M53 228h24v6H49c0-3 2-5 4-6zM93 228h24v6H92z" fill="#1f3037" />
        <rect x="49" y="108" width="82" height="59" rx="6" transform="rotate(8 90 138)" fill="#a8ba70" />
      </g>
      <g className="person-mid">
        <circle cx="169" cy="83" r="15" fill="#ffad45" />
        <path d="M157 72c7-13 28-10 31 5 3 10-3 21-11 21-5-10-14-12-20-26z" fill="#1f3037" />
        <path d="M157 96h25l4 36h-35z" fill="#ffad45" />
        <path d="M136 120c10-18 41-26 60-6 10 11 10 32 5 55h-67c-3-20-5-36 2-49z" fill="#ffad45" />
        <path d="M139 167h23l-8 64h-20zM178 166h22l18 61h-20z" fill="#26363b" />
        <path d="M130 229h26v7h-27c0-3 0-5 1-7zM198 226h27v8h-26z" fill="#26363b" />
        <rect x="114" y="111" width="74" height="55" rx="6" transform="rotate(-13 151 139)" fill="#eef1d6" />
      </g>
      <g className="person-right">
        <circle cx="236" cy="91" r="15" fill="#ffad45" />
        <path d="M225 78c11-15 30-4 30 14 0 12 10 19 8 35-20 3-41-2-47-19-4-12 0-23 9-30z" fill="#24363b" />
        <path d="M220 112c17-11 42-4 49 18l-5 64h-53z" fill="#24363b" />
        <path d="M203 128c-8 13-8 30 4 39l12-13c-5-8-4-16 0-23zM268 130c13 12 16 29 8 42l-14-12c4-9 2-17-2-24z" fill="#ffad45" />
        <path d="M218 194h16l-3 35h-16zM248 194h16l21 34h-18z" fill="#ffad45" />
        <path d="M212 229h24v6h-27c0-3 1-5 3-6zM267 228h23v6h-31z" fill="#24363b" />
        <rect x="220" y="116" width="58" height="55" rx="5" transform="rotate(-7 249 144)" fill="#879456" />
      </g>
      <path d="M150 19c5-12 13-17 24-16-1 11-9 18-24 16z" fill="#81954d" />
      <path d="M143 26c-2-9 1-16 9-22 5 9 2 16-9 22z" fill="#b8c876" />
    </svg>
  );
}

function LocationIllustration() {
  return (
    <svg className="location-art" viewBox="0 0 260 205" role="img" aria-label="동네 위치 인증">
      <rect x="12" y="20" width="205" height="130" rx="7" fill="#26363b" />
      <rect x="25" y="28" width="176" height="114" fill="#f1f1ee" />
      <path d="M45 31l35 110M111 28l-10 116M166 28l-18 114" stroke="#fff" strokeWidth="12" />
      <path d="M25 80l176-26M31 127l168-23" stroke="#fff" strokeWidth="10" />
      <circle cx="18" cy="87" r="4" fill="#738681" />
      <circle cx="207" cy="88" r="6" fill="#738681" />
      <path d="M74 58c0 13-16 25-16 25S42 71 42 58a16 16 0 1 1 32 0z" fill="#fca42b" />
      <circle cx="58" cy="58" r="6" fill="#fff" />
      <path d="M106 34c0 12-15 23-15 23S76 46 76 34a15 15 0 0 1 30 0zM218 36c0 9-11 18-11 18s-11-9-11-18a11 11 0 0 1 22 0zM87 113c0 9-11 18-11 18s-11-9-11-18a11 11 0 0 1 22 0z" fill="#b1bf72" />
      <circle cx="91" cy="34" r="5" fill="#fff" />
      <circle cx="207" cy="36" r="4" fill="#fff" />
      <circle cx="76" cy="113" r="4" fill="#fff" />
      <rect x="86" y="91" width="60" height="14" rx="7" fill="#fff" />
      <text x="99" y="101" fill="#1d282c" fontSize="7" fontWeight="800">SHOP</text>
      <circle cx="137" cy="98" r="4" fill="none" stroke="#1d282c" strokeWidth="1.2" />
      <path d="M140 101l4 4" stroke="#1d282c" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M85 150h72" stroke="#b9b9b3" strokeWidth="1" />
      <path d="M40 146l-21 35h44z" fill="#aebd72" />
      <path d="M45 132v54" stroke="#677350" strokeWidth="4" />
      <rect x="21" y="165" width="47" height="28" fill="#e4ecce" />
      <g transform="translate(145 46)">
        <path d="M34 8c25 4 38 31 33 58-6 34-14 63-6 91H19c2-24-2-51-14-81C-7 44 5 3 34 8z" fill="#ffad45" />
        <circle cx="37" cy="34" r="21" fill="#ffb35a" />
        <path d="M16 28C20 3 54-2 66 18c9 15 3 33-8 42C47 41 34 32 16 28z" fill="#25363c" />
        <path d="M44 72c30 11 38 50 17 88H17C5 128 10 85 44 72z" fill="#ffad45" />
        <path d="M18 88c-10 21-18 48-31 70l17 7c18-22 28-46 32-70z" fill="#ffb35a" />
        <rect x="17" y="83" width="32" height="51" rx="6" transform="rotate(-17 33 108)" fill="#26363b" />
      </g>
    </svg>
  );
}

function CompleteIllustration() {
  return (
    <svg className="complete-art" viewBox="0 0 250 240" role="img" aria-label="공동구매 준비 완료">
      <rect x="22" y="92" width="36" height="33" fill="#eeeeeb" />
      <path d="M29 101h20l-3 16H32zM28 98h22" stroke="#d8d8d4" strokeWidth="3" />
      <rect x="175" y="41" width="55" height="84" rx="5" fill="#e6e8e5" />
      <rect x="188" y="50" width="13" height="11" rx="2" fill="#b1bf72" />
      <rect x="214" y="50" width="12" height="4" rx="2" fill="#fff" />
      <rect x="206" y="64" width="20" height="4" rx="2" fill="#fff" />
      <circle cx="202" cy="83" r="3" fill="#c5c8c1" />
      <circle cx="215" cy="83" r="3" fill="#c5c8c1" />
      <rect x="61" y="29" width="88" height="180" rx="13" fill="#26363b" />
      <rect x="69" y="44" width="72" height="148" fill="#f8f8f3" />
      <rect x="91" y="35" width="28" height="3" rx="2" fill="#fff" />
      <g fill="#b1bf72">
        <rect x="76" y="56" width="21" height="28" />
        <rect x="105" y="56" width="21" height="28" />
        <rect x="76" y="96" width="21" height="28" />
        <rect x="105" y="96" width="21" height="28" />
      </g>
      <g fill="#26363b">
        <path d="M80 62l15 9-4 8-12-10z" />
        <path d="M110 62l13 10-4 8-11-10z" />
        <path d="M83 101h11v18H80zM108 101h13v18h-13z" />
      </g>
      <text x="82" y="91" fill="#777" fontSize="7">2,000</text>
      <text x="110" y="91" fill="#777" fontSize="7">5,000</text>
      <rect x="79" y="146" width="52" height="16" rx="2" fill="#26363b" />
      <text x="87" y="157" fill="#fff" fontSize="7" fontWeight="800">ADD TO CART</text>
      <circle cx="92" cy="215" r="7" fill="#59666a" />
      <circle cx="131" cy="215" r="7" fill="#59666a" />
      <path d="M67 178h82l-8 30H76z" fill="none" stroke="#26363b" strokeWidth="5" />
      <path d="M56 166h22" stroke="#26363b" strokeWidth="5" strokeLinecap="round" />
      <g transform="translate(142 49)">
        <circle cx="39" cy="25" r="18" fill="#ffb35a" />
        <path d="M22 20c3-22 29-26 43-9 10 12 6 26 0 34-10-17-24-20-43-25z" fill="#24363b" />
        <path d="M29 45h23l10 70H19z" fill="#ffad45" />
        <path d="M22 79c-20 8-40 17-61 27l8 15c26-8 49-18 67-32zM58 77c10 17 15 40 17 70H58c-5-24-11-44-22-59z" fill="#ffb35a" />
        <path d="M25 115h25l-4 84H25zM54 115h23l20 84H76z" fill="#26363b" />
        <path d="M22 199h27v7H20zM77 199h28v7H75z" fill="#fca42b" />
      </g>
      <path d="M32 167c-9 14-11 29-5 48 14-11 19-27 5-48zM24 192c-12 3-20 12-23 27 15 0 25-9 23-27z" fill="#aebd72" />
      <rect x="14" y="211" width="35" height="16" fill="#26363b" />
    </svg>
  );
}

function Welcome({ onNext }) {
  return (
    <PhoneFrame title="로그인">
      <section className="welcome-screen">
        <NonaLogo />
        <h1>혼자보다 가벼운 소비,<br />가까운 동네와 함께 시작해보세요.</h1>
        <p>근처 사람들과 필요한 물건을 함께 구매하고<br />남는 소비를 줄여보세요</p>
        <WelcomeIllustration />
        <button className="main-button" type="button" onClick={onNext}>전화번호로 시작하기</button>
        <p className="terms">로그인 후 Nona의 이용약관 및 개인정보 처리방침에<br />동의하는 것으로 간주됩니다.</p>
      </section>
    </PhoneFrame>
  );
}

function PhoneScreen({ phone, setPhone, onBack, onNext }) {
  const formatted = phone.replace(/[^\d]/g, '').slice(0, 11).replace(/(\d{3})(\d{4})(\d{0,4})/, (_, a, b, c) => (c ? `${a}-${b}-${c}` : `${a}-${b}`));

  function submit(event) {
    event.preventDefault();
    if (phone.replace(/[^\d]/g, '').length >= 10) onNext();
  }

  return (
    <PhoneFrame title="전화번호">
      <form className="form-screen" onSubmit={submit}>
        <Header title="전화번호를 입력해주세요" onBack={onBack} step={0} />
        <p className="subcopy">인증번호를 보내드릴게요.</p>
        <label className="line-input">
          <Phone size={16} />
          <input value={formatted} inputMode="numeric" onChange={(event) => setPhone(event.target.value)} placeholder="010-1234-5678" />
        </label>
        <button className="main-button square" type="submit">인증번호 받기</button>
        <aside className="notice">
          <strong>ⓘ 안내사항</strong>
          <p>같은 동네 사람들과 안전하게 거래할 수 있도록<br />전화번호 인증 후 이용이 가능합니다.</p>
        </aside>
      </form>
    </PhoneFrame>
  );
}

function CodeScreen({ code, setCode, phone, onBack, onNext }) {
  const digits = code.padEnd(6, ' ').slice(0, 6).split('');

  function update(index, value) {
    const next = digits.map((digit, i) => (i === index ? value.replace(/\D/g, '').slice(-1) : digit.trim())).join('');
    setCode(next.slice(0, 6));
  }

  function submit(event) {
    event.preventDefault();
    if (code.length === 6) onNext();
  }

  return (
    <PhoneFrame title="인증번호">
      <form className="form-screen" onSubmit={submit}>
        <Header title={<>인증번호를<br />입력해주세요</>} onBack={onBack} step={1} />
        <p className="subcopy">{phone || '010-1234-5678'}으로 인증번호를 보냈어요</p>
        <div className="code-grid">
          {digits.map((digit, index) => (
            <input key={index} aria-label={`${index + 1}번째 인증번호`} inputMode="numeric" maxLength="1" value={digit.trim()} onChange={(event) => update(index, event.target.value)} />
          ))}
        </div>
        <button className="main-button square" type="submit">인증번호 받기</button>
        <button className="link-button" type="button" onClick={() => setCode('')}>30초 후 다시 보내기</button>
      </form>
    </PhoneFrame>
  );
}

function NicknameScreen({ nickname, setNickname, onBack, onNext }) {
  function submit(event) {
    event.preventDefault();
    if (nickname.trim().length > 0) onNext();
  }

  return (
    <PhoneFrame title="닉네임 설정">
      <form className="form-screen" onSubmit={submit}>
        <Header title={<>사용할 닉네임을<br />설정해주세요</>} onBack={onBack} step={2} />
        <p className="subcopy">다른 사용자에게 표시돼요.</p>
        <label className="line-input nickname-input">
          <UserRound size={17} />
          <input value={nickname} maxLength="10" onChange={(event) => setNickname(event.target.value)} placeholder="닉네임" />
          <b>{nickname.length}/10</b>
        </label>
        <button className="main-button square" type="submit">다음</button>
      </form>
    </PhoneFrame>
  );
}

function LocationScreen({ onBack, onNext }) {
  const [area, setArea] = useState('');

  return (
    <PhoneFrame title="로그인">
      <section className="location-screen">
        <button className="back-button" type="button" onClick={onBack} aria-label="뒤로가기">
          <ChevronLeft size={21} />
        </button>
        <StepDots active={2} />
        <section className="copy-block location-copy">
          <h1>가까운 곳에서의 거래를 위해<br />동네 인증이 필요해요</h1>
          <p>현재 위치를 기반으로<br />가까운 동네의 공동구매를 보여드려요!</p>
        </section>
        <LocationIllustration />
        <label className="area-box">
          <MapPin size={15} />
          <input value={area} onChange={(event) => setArea(event.target.value)} placeholder="동네 입력" />
          <button type="button" onClick={() => {}}>변경하기</button>
        </label>
        <button className="main-button" type="button" onClick={onNext}>현재 위치로 인증하기</button>
        <p className="terms">위치 정보는 동네 인증 용도로만 사용돼요</p>
      </section>
    </PhoneFrame>
  );
}

function CompleteScreen({ onStart }) {
  return (
    <PhoneFrame title="로그인">
      <section className="complete-screen">
        <h1>첫 공동구매 준비 완료!<br />가입이 완료되었어요!</h1>
        <p>이제 가까운 사람들과<br />함께 필요한 물건을 나눠보세요</p>
        <CompleteIllustration />
        <button className="main-button" type="button" onClick={onStart}>시작하기</button>
        <p className="terms">위치 정보는 동네 인증 용도로만 사용돼요</p>
      </section>
    </PhoneFrame>
  );
}

function App() {
  const [screen, setScreen] = useState('welcome');
  const [phone, setPhone] = useState('01012345678');
  const [code, setCode] = useState('');
  const [nickname, setNickname] = useState('공규없나공규');

  const index = screens.indexOf(screen);
  const goNext = () => setScreen(screens[Math.min(index + 1, screens.length - 1)]);
  const goBack = () => setScreen(screens[Math.max(index - 1, 0)]);

  if (screen === 'welcome') return <Welcome onNext={goNext} />;
  if (screen === 'phone') return <PhoneScreen phone={phone} setPhone={setPhone} onBack={goBack} onNext={goNext} />;
  if (screen === 'code') return <CodeScreen code={code} setCode={setCode} phone={phone} onBack={goBack} onNext={goNext} />;
  if (screen === 'nickname') return <NicknameScreen nickname={nickname} setNickname={setNickname} onBack={goBack} onNext={goNext} />;
  if (screen === 'location') return <LocationScreen onBack={goBack} onNext={goNext} />;
  return <CompleteScreen onStart={() => setScreen('welcome')} />;
}

createRoot(document.getElementById('root')).render(<App />);
