const api = 'http://localhost:5000';

async function getUsers() {
  const res = await fetch(api + '/users');
  const data = await res.json();
  console.log(data);
}

function onRegisterFormSubmit(event) {
  event.preventDefault();

  const username = document.getElementById('username').value;
  const cpf = document.getElementById('cpf').value;
  const password = document.getElementById('password').value;

  const url = api + '/register'

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, cpf, password }),
  })
    .then(async (response) => {
      if (!response.ok) {
        const reason = await response.text()
        const msg = `Erro ao registrar usuário? ${reason}`
        alert(msg)
        throw new Error(msg);
      }
      return response.json();
    })
    .then((data) => {
      console.log('Usuário registrado:', data);
      alert(`Usuário registrado com sucesso\nusername: ${data.username}\ncpf: ${data.cpf}`);
      window.location.href = '/login';
    })
    .catch((error) => {
      console.error('Erro:', error);
    });

  return false;
}
