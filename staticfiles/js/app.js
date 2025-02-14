document.addEventListener("DOMContentLoaded", function() {
    let index = 0; 
    
    const computeForm = document.getElementById('compute-form');
    const runForm = document.getElementById('run-form');        
    let computedPlan = null;


    const taskRadios = document.querySelectorAll('input[name="data_source"]');
    const taskDescriptionDiv = document.getElementById('task-description');
    // const uploadForm = document.getElementById('upload-form');
    const spinner = document.querySelector('.spinner-border'); // Get the spinner element
    const resultsDiv = document.getElementById('results'); // The div where results are displayed
    const fileSocket = new WebSocket('ws://' + window.location.host + '/ws/files/');

    fileSocket.onopen = function(e) {
        console.log("FileSocket connection established");
    };

    fileSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';  // Clear the list
        data.files.forEach(file => {
            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item', 'd-flex', 'align-items-center');

            // Create an icon based on the file type
            const icon = document.createElement('i');
            icon.classList.add('file-icon');

            if (file.type === 'pdf') {
                icon.classList.add('fas', 'fa-file-pdf');  // Font Awesome PDF icon
            } else if (file.type === 'excel') {
                icon.classList.add('fas', 'fa-file-excel');  // Font Awesome Excel icon
            } else if (file.type === 'word') {
                icon.classList.add('fas', 'fa-file-word');  // Font Awesome Word icon
            } else {
                icon.classList.add('fas', 'fa-file');  // Generic file icon
            }

            listItem.appendChild(icon);
            listItem.appendChild(document.createTextNode(file.name));

            fileList.appendChild(listItem);
        });
    };

    fileSocket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    let taskId = null;

    taskRadios.forEach(radio => {
        radio.addEventListener('change', function(event) {
            const selectedTask = this.value;
            fileSocket.send(JSON.stringify({ task: selectedTask }));
            console.log(fileSocket)
            taskId = event.target.value;
            const socket = new WebSocket('ws://' + window.location.host + '/ws/task_description/');

            socket.onopen = function(e) {
                const message = {
                    'task_id': taskId
                };
                console.log("Sending message:", JSON.stringify(message));
                socket.send(JSON.stringify(message));
            };

            socket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                taskDescriptionDiv.innerHTML = data.task_description;
            };

            socket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };

            socket.onclose = function(e) {
                console.log('WebSocket closed:', e);
            };
        });
    });

    // uploadForm.addEventListener('submit', function(event) {
    //     event.preventDefault();

    //     // Show the spinner
    //     spinner.style.display = 'block';

    //     const formData = new FormData(uploadForm);

    //     fetch('/upload/', {
    //         method: 'POST',
    //         body: formData,
    //         headers: {
    //             'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    //         }
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         console.log('Success:', data);
    //         spinner.style.display = 'none'; // Hide the spinner
    //     })
    //     .catch((error) => {
    //         console.error('Error:', error);
    //         spinner.style.display = 'none'; // Hide the spinner on error
    //     });
    //     });
    


    computeForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const dataSource = document.querySelector('input[name="data_source"]:checked').value;
        const policy = document.getElementById('id_policy').value;
        const executionEngine = document.getElementById('id_execution_engine').value;

        const socket = new WebSocket('ws://' + window.location.host + '/ws/compute/');

        socket.onopen = function(e) {
            socket.send(JSON.stringify({
                'data_source': dataSource,
                'policy': policy,
                'execution_engine': executionEngine,
            }));
        };

        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            const planDiv = document.getElementById('plan');
            planDiv.style.overflowY = 'auto';
            planDiv.style.height = '200px'; // Adjust height as needed   

            const noResultsMessage = document.getElementById('no-plan-message');
            if (noResultsMessage) {
                noResultsMessage.remove();
            }
            const planText = document.getElementById('plan-text');
            if (planText) {
                planText.remove();
            }

            
            planDiv.innerHTML += '<p id="plan-text">' + data.plan.replace(/\n/g, '<br>') + '</p>';
    
            computedPlan = data.plan;
    
        }

        socket.onclose = function(e) {
            console.error('WebSocket closed unexpectedly');
        };
    });

runForm.addEventListener('submit', function(event){
    event.preventDefault();
    if (!computedPlan) {
        alert('Please compute a plan first');
        return;
    }
    // Clear previous results
    const resultDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p id="no-results-message">Running plan, please wait...</p>';

    const spinner = document.querySelector('.spinner-border'); // Get the spinner element
    spinner.style.display = 'block';
    const socket = new WebSocket('ws://' + window.location.host + '/ws/run/');

    socket.onopen = function(e){
        const useCache = document.getElementById('use_cache').checked;
        const message = {
            'task': taskId,
            'plan': computedPlan,
            'use_cache': useCache,
            'policy': document.getElementById('id_policy').value,
        };
        socket.send(JSON.stringify(message));
    };
    
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const resultDiv = document.getElementById('results');
        resultDiv.style.overflowY = 'auto';
        resultDiv.style.height = '500px'; // Adjust height as needed

        resultsDiv.innerHTML = '';  // Clear the message about running plan

        if (data.finished) {
            console.log("Finished here are stats", data.stats)
            // Add the content of the stats variable to the results container
            const statsSection = document.createElement('div');
            statsSection.classList.add('mt-4');
            statsSection.innerHTML = '<h5>Execution Stats:</h5><p>' + data.stats.replace(/\n/g, '<br>') + '</p>';
            resultsDiv.appendChild(statsSection);
        }

        if (data.records.length > 0) {
            const noResultsMessage = document.getElementById('no-results-message');
            if (noResultsMessage) {
                noResultsMessage.remove();
            }

            let table = document.querySelector('#results table');
            if (!table) {
                table = document.createElement('table');
                table.classList.add('table', 'table-striped', 'mt-3', 'results-table');
                const thead = table.createTHead();
                const headRow = thead.insertRow();
        
                // Assuming all records have the same structure, use the first record to get column names
                const columns = Object.keys(data.records[0]);
                columns.forEach(column => {
                    const th = document.createElement('th');
                    th.textContent = column;
                    headRow.appendChild(th);
                });

                resultDiv.appendChild(table);
            }

            const tbody = table.tBodies[0] || table.createTBody();

            // Append new rows to the existing table
            data.records.forEach(record => {
                const row = tbody.insertRow();
                const columns = Object.keys(record);
                columns.forEach(column => {
                    const cell = row.insertCell();
                    cell.textContent = record[column];
                });
            });
        }
        // resultDiv.innerHTML += '<p>' + data.stats + '</p>';
        index++;
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
        spinner.style.display = 'none'; // Hide the spinner on error
    };

    socket.onclose = function(e){
        spinner.style.display = 'none';
        console.error('WebSocket closed unexpectedly');
    };
});
});
