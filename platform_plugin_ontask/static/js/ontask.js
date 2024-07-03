const createWorkflow = $('#create-workflow');
const uploadDataframe = $('#upload-dataframe');

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

createWorkflow.on('click', () => {
  const { courseId } = createWorkflow.data();
  fetch(`platform-plugin-ontask/${courseId}/api/v1/workflow/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((errorData) => {
          throw new Error(
            errorData.error || 'Something went wrong. Please try again.'
          );
        });
      }
      window.location.reload();
    })
    .catch((error) => {
      $('#create-workflow-error-message')
        .text(error.message)
        .removeClass('hidden');
    });
});

let timeoutId;

uploadDataframe.on('click', () => {
  const { courseId } = uploadDataframe.data();
  fetch(`platform-plugin-ontask/${courseId}/api/v1/table/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
  })
    .then((response) => {
      if (!response.ok) {
        const errorData = response.json();
        throw new Error(
          errorData.error || 'Something went wrong. Please try again.'
        );
      }

      $('#upload-dataframe-message').text(
        'Loading dataframe... Please wait a few minutes.'
      );

      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        $('#upload-dataframe-message').text('');
      }, 2000);

      document.location.reload();
    })
    .catch((error) => {
      $('#upload-dataframe-message').text(error.message);
    });
});
