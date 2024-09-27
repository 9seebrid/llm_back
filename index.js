const express = require('express'); // express 모듈 불러오기
const cors = require('cors'); // cors 모듈 불러오기
const PORT = 8000; // 포트 설정
const { spawn } = require('child_process'); // child_process 모듈 불러오기
const path = require('path'); // path 모듈 불러오기
const bodyParser = require('body-parser');

console.log(path.join(__dirname));

const app = express(); // express 모듈을 사용하기 위해 app 변수에 할당

app.use(bodyParser.json());
app.use(cors()); // cors 사용 설정 http, https 프로토콜을 사용하는 서버간의 통신을 허용한다
app.use(express.json()); // json 형식 사용 설정

const corsOptions = {
  origin: 'http://localhost:3000 ', // 클라이언트의 주소를 명시
  credentials: true, // 자격 증명 허용
};

app.use(cors(corsOptions));

app.get('/', (req, res) => {
  res.send('Hello World! node'); // get 요청 시 Hello World! 출력
});

app.post('/chat', (req, res) => {
  const sendQuestion = req.body.question; // 클라이언트에서 받은 질문을 변수에 할당

  const execPython = path.join(__dirname, 'bizchat.py'); // 파이썬 파일 경로 설정)
  const pythonPath = path.join(__dirname, 'bin', 'python3'); // 파이썬 파일 경로 설정
  const result = spawn(pythonPath, [execPython, sendQuestion]); // 파이썬 파일 수행

  output = '';

  //파이썬 파일 수행 결과를 받아온다
  result.stdout.on('data', function (data) {
    output += data.toString();
  });

  result.on('close', (code) => {
    if (code === 0) {
      res.status(200).json({ answer: output });
    } else {
      res.status(500).send('Internal Server Error');
    }
  });

  result.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });
});

app.listen(PORT, () => console.log(`Server is runnig on ${PORT}`)); // 서버 실행 시 메세지 출력
