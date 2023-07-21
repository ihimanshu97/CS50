document.addEventListener('DOMContentLoaded', function () {

	// Use buttons to toggle between views
	document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
	document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
	document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
	document.querySelector('#compose').addEventListener('click', compose_email);

	const form = document.getElementById('compose-form')

	form.addEventListener('submit', (e) => {
		e.preventDefault()
		fetch('/emails', {
			method: 'POST',
			body: JSON.stringify({
				recipients: document.querySelector('#compose-recipients').value,
				subject: document.querySelector('#compose-subject').value,
				body: document.querySelector('#compose-body').value
			})
		})
			.then(res => res.json())
			.then(result => load_mailbox('sent'));
	})

	// By default, load the inbox
	load_mailbox('inbox');
});

function compose_email() {

	// Show compose view and hide other views
	document.querySelector('#emails-view').style.display = 'none';
	document.querySelector('#email-view').style.display = 'none';
	document.querySelector('#compose-view').style.display = 'block';

	// Clear out composition fields
	document.querySelector('#compose-recipients').value = '';
	document.querySelector('#compose-subject').value = '';
	document.querySelector('#compose-body').value = '';
}

function load_mail(id, mailbox) {
	document.querySelector('#emails-view').style.display = 'none';
	document.querySelector('#email-view').style.display = 'block';
	document.querySelector('#compose-view').style.display = 'none';

	fetch(`/emails/${id}`)
		.then(res => res.json())
		.then(email => {
			document.querySelector('#email-view').innerHTML = `
				<div><b>From: </b> ${email.sender}</div>
				<div><b>To: </b> ${email.recipients.toString()}</div>
				<div><b>Subject: </b> ${email.subject}</div>
				<div><b>Time: </b> ${email.timestamp}</div>
				<div class="my-2">
					<button type="button" class="btn btn-sm btn-danger">
						<i class="bi bi-reply"></i> Reply
					</button>
					${mailbox !== 'sent' ?
					`<button type="button" class="btn btn-sm btn-outline-danger">
						<i class="bi bi-archive"></i>
						${email.archived ? 'Unarchive' : 'Archive'}
						</button>` : ''
				}
				</div>
				<hr>
				<pre>${email.body}</pre>
			`

			const btns = document.querySelector('#email-view').querySelectorAll('.btn')

			btns[0].addEventListener('click', () => {
				compose_email()
				document.querySelector('#compose-recipients').value = email.sender;
				document.querySelector('#compose-subject').value = email.subject.startsWith('Re: ') ? email.subject : 'Re: ' + email.subject;
				document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
			})

			if (btns[1]) {
				btns[1].addEventListener('click', () => {
					fetch(`/emails/${email.id}`, {
						method: 'PUT',
						body: JSON.stringify({
							archived: !email.archived
						})
					})
					load_mailbox('inbox')
				})
			}

			fetch(`/emails/${email.id}`, {
				method: 'PUT',
				body: JSON.stringify({
					read: true
				})
			})
		})
}

function load_mailbox(mailbox) {

	// Show the mailbox and hide other views
	document.querySelector('#emails-view').style.display = 'block';
	document.querySelector('#email-view').style.display = 'none';
	document.querySelector('#compose-view').style.display = 'none';

	// Show the mailbox name
	document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

	fetch(`/emails/${mailbox}`)
		.then(res => res.json())
		.then(data => {

			const table = document.createElement('table')
			table.classList.add('table')
			table.classList.add('table-stripped')
			table.classList.add('table-hover')
			table.classList.add('table-bordered')

			table.innerHTML = `
				<thead>
					<tr>
						<th scope="col">Sender</th>
						<th scope="col">Subject</th>
						<th scope="col">Time</th>
					</tr>
				</thead>
			`

			const tbody = document.createElement('tbody')

			data.forEach(email => {
				const tr = document.createElement('tr')

				if (!email.read) {
					tr.classList.add('unread')
				}

				tr.innerHTML = `
					<td>${email.sender}</td>
					<td>${email.subject}</td>
					<td>${email.timestamp}</td>
				`

				tr.addEventListener('click', () => {
					load_mail(email.id, mailbox)
				})
				tbody.appendChild(tr)
			})

			table.appendChild(tbody)

			document.querySelector('#emails-view').appendChild(table)
		})
}