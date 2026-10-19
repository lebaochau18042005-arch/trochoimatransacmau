/* Optional no-API-cost AI assistant for teacher create page.
   Copies a prompt for use in ChatGPT and imports teacher-reviewed JSON.
   Never sends classroom data or secrets to an external AI provider. */
(() => {
  const el = (tag, props = {}, text = '') => {
    const n = document.createElement(tag);
    Object.assign(n, props);
    if (text) n.textContent = text;
    return n;
  };
  const promptFor = (topic, subject, grade, count) =>
    'Bạn là giáo viên có kinh nghiệm, bám CTGDPT 2018. Hãy đề xuất ' + count +
    ' câu hỏi trắc nghiệm môn ' + subject + ' lớp ' + grade + ' chủ đề "' + topic +
    '". Mỗi câu có 4 phương án và một đáp án đúng. Không bịa thông tin; nếu không chắc, ghi cần kiểm chứng. ' +
    'Chỉ xuất JSON hợp lệ (không Markdown), dạng mảng: ' +
    '[{"text":"Nội dung câu hỏi","options":["A","B","C","D"],"answer":0}]. ' +
    'answer là vị trí đáp án đúng tính từ 0 đến 3. Giáo viên sẽ thẩm định trước khi phát hành.';
  function setup() {
    const root = document.querySelector('#questionList');
    if (!root || document.querySelector('#aiHelper')) return;
    const panel = el('section', {id:'aiHelper', className:'card'});
    panel.style.cssText = 'margin:14px 0;padding:16px;border:1px solid #b7d8d1;border-radius:12px';
    panel.append(el('h3', {}, 'AI gợi ý câu hỏi (miễn phí, giáo viên duyệt)'));
    panel.append(el('p', {}, 'Sao chép yêu cầu sang ChatGPT, rồi dán JSON kết quả vào đây. WebApp không gửi dữ liệu học sinh ra ngoài.'));
    const topic = el('input',{id:'aiTopic',placeholder:'Tên bài/chủ đề, ví dụ Thiên nhiên nhiệt đới ẩm gió mùa'});
    const grade = el('select',{id:'aiGrade'});
    ['10','11','12'].forEach(v=>{const o=el('option',{value:v},'Lớp '+v);if(v==='12')o.selected=true;grade.append(o)});
    const count = el('select',{id:'aiCount'});
    [5,10,15,20].forEach(v=>count.append(el('option',{value:String(v)},v+' câu')));
    count.value='10';
    const copy = el('button',{type:'button'},'Sao chép yêu cầu AI');
    const paste = el('textarea',{id:'aiJson',rows:5,placeholder:'Dán mảng JSON câu hỏi do AI tạo vào đây'});
    paste.style.width='100%';
    const importBtn = el('button',{type:'button'},'Kiểm tra và nhập câu hỏi');
    const status=el('p',{id:'aiStatus',role:'status'});
    panel.append(topic,grade,count,copy,paste,importBtn,status);
    root.parentNode.insertBefore(panel,root);
    copy.addEventListener('click',async()=>{
      const t=topic.value.trim(),s=document.querySelector('#gameSubject')?.value.trim()||'Địa lí';
      if(!t){status.textContent='Hãy nhập tên chủ đề trước.';return}
      try{await navigator.clipboard.writeText(promptFor(t,s,grade.value,count.value));status.textContent='Đã sao chép. Dán yêu cầu vào ChatGPT để nhận JSON.'}
      catch{status.textContent='Không thể sao chép tự động. Hãy kiểm tra quyền clipboard của trình duyệt.'}
    });
    importBtn.addEventListener('click',()=>{
      let items;
      try{items=JSON.parse(paste.value)}
      catch{status.textContent='JSON chưa hợp lệ. Hãy yêu cầu AI chỉ xuất mảng JSON, không có dấu ```.';return}
      if(!Array.isArray(items)||!items.length||items.length>100||items.some(q=>
        !q||typeof q.text!=='string'||!q.text.trim()||q.text.length>1000||
        !Array.isArray(q.options)||q.options.length!==4||
        q.options.some(o=>typeof o!=='string'||!o.trim()||o.length>1000)||
        !Number.isInteger(q.answer)||q.answer<0||q.answer>3)){
        status.textContent='Cấu trúc không hợp lệ: mỗi câu cần text, 4 options và answer từ 0 đến 3.';return
      }
      if(!window.confirm('Thay toàn bộ câu hỏi đang nhập bằng '+items.length+' câu mới? Hãy kiểm tra nội dung và đáp án trước khi phát hành.'))return;
      const list=document.querySelector('#questionList');
      while(list.querySelector('[data-remove]') && list.querySelectorAll('.question').length>1)
        list.querySelector('[data-remove]').click();
      const add=document.querySelector('#addQ');
      for(let i=1;i<items.length;i++)add.click();
      items.forEach((q,i)=>{
        const textInput=list.querySelector('[data-q="'+i+'"][data-field="text"]');
        textInput.value=q.text;textInput.dispatchEvent(new Event('input',{bubbles:true}));
        q.options.forEach((v,j)=>{
          const inp=list.querySelector('[data-q="'+i+'"][data-option="'+j+'"]');
          inp.value=v;inp.dispatchEvent(new Event('input',{bubbles:true}));
        });
        const correct=list.querySelector('[data-correct="'+i+'"][value="'+q.answer+'"]');
        correct.checked=true;correct.dispatchEvent(new Event('change',{bubbles:true}));
      });
      status.textContent='Đã nhập '+items.length+' câu. Giáo viên cần rà soát từng đáp án trước khi phát hành.';
    });
  }
  const observer=new MutationObserver(setup);
  observer.observe(document.getElementById('app'),{childList:true,subtree:false});
  setup();
})();
