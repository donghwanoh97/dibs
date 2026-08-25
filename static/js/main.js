document.addEventListener('DOMContentLoaded', ()=>{
    const verifyBtn = document.getElementById('verify-btn');
    const resultID = document.getElementById('result-id');

    verifyBtn.addEventListener('click', () => {
        // hidden 클래스를 제거하여 ID를 표시
        resultID.classList.remove('hidden');

        // 백엔드 연동 전 임시 텍스트 변경 테스트
        resultID.textContent = "당신의 ID: asdf";
    })
})