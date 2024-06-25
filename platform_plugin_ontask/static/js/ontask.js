const createWorkflow = $('#create-workflow');
const updateWorkflow = $('#update-workflow');

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
        const errorData = response.json();
        throw new Error(
          errorData.error || 'Something went wrong. Please try again.'
        );
      }
      return response.json();
    })
    .then((data) => {
      console.log('Created workflow:', data);
      window.location.reload();
    })
    .catch((error) => {
      $('#create-workflow-error-message').text(error.message);
    });
});

updateWorkflow.on('click', () => {
  const { courseId } = updateWorkflow.data();
  fetch(`platform-plugin-ontask/${courseId}/api/v1/workflow/`, {
    method: 'PATCH',
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
      return response.json();
    })
    .then((data) => {
      console.log('Updated workflow:', data);
    })
    .catch((error) => {
      $('#update-workflow-error-message').text(error.message);
    });
});
