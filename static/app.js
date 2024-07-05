document.addEventListener('DOMContentLoaded', () => {
    const statusElement = document.getElementById('status');
    const quizCard = document.getElementById('quiz-card');
    const quizWord = document.getElementById('quiz-word');
    const quizOptions = document.getElementById('quiz-options');
    const quizResult = document.getElementById('quiz-result');
    const startQuizButton = document.getElementById('start-quiz');
    const nextQuestionButton = document.getElementById('next-question');
  
    let words = [];
    let currentQuizIndex = 0;
    let quizWords = [];
  
    fetch('/api/words')
      .then(response => response.json())
      .then(data => {
        statusElement.textContent = '単語の読み込みに成功しました。';
        words = data;
      })
      .catch(error => {
        statusElement.textContent = '単語の読み込みに失敗しました: ' + error;
      });
  
    startQuizButton.addEventListener('click', () => {
      const quizCount = parseInt(document.getElementById('quiz-count').value, 10);
      quizWords = getRandomWords(quizCount);
      currentQuizIndex = 0;
      quizCard.classList.remove('hidden');
      startQuizButton.classList.add('hidden');
      nextQuestion();
    });
  
    nextQuestionButton.addEventListener('click', nextQuestion);

    // Enterキーで次の問題に進む
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !nextQuestionButton.classList.contains('hidden')) {
        nextQuestion();
      }
    });
  
    function nextQuestion() {
      quizResult.textContent = '';
      nextQuestionButton.classList.add('hidden');
      if (currentQuizIndex >= quizWords.length) {
        quizCard.classList.add('hidden');
        startQuizButton.classList.remove('hidden');
        return;
      }
      const randomWord = quizWords[currentQuizIndex];
      quizWord.textContent = randomWord.word;
  
      const options = shuffleArray(words.map(word => word.meaning).filter(opt => opt !== randomWord.meaning));
      const correctAnswerIndex = Math.floor(Math.random() * 4);
      options.splice(correctAnswerIndex, 0, randomWord.meaning);
  
      quizOptions.innerHTML = '';
      options.slice(0, 4).forEach(option => {
        const optionButton = document.createElement('button');
        optionButton.textContent = option;
        optionButton.addEventListener('click', () => {
          if (option === randomWord.meaning) {
            optionButton.classList.add('correct');
            quizResult.textContent = 'Correct!';
            quizResult.style.color = 'green';
          } else {
            optionButton.classList.add('incorrect');
            quizResult.textContent = `Incorrect. The correct answer is "${randomWord.meaning}".`;
            quizResult.style.color = 'red';
          }
          Array.from(quizOptions.children).forEach(button => {
            button.disabled = true;
            if (button.textContent === randomWord.meaning) {
              button.classList.add('correct');
            }
          });

          fetch('/quiz', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              answer: option,
              correct_answer: randomWord.meaning,
              word_id: randomWord.id
            })
          }).then(response => response.json())
            .then(data => {
              if (data.success) {
                nextQuestionButton.classList.remove('hidden');
                currentQuizIndex++;
              }
            });
        });
        quizOptions.appendChild(optionButton);
      });
    }
  
    function getRandomWords(count) {
      const shuffledWords = shuffleArray([...words]);
      return shuffledWords.slice(0, count);
    }
  
    function shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    }
  });
