document.addEventListener("DOMContentLoaded", function() {
    let index = 0; 
    
    const computeForm = document.getElementById('compute-form');
    const runForm = document.getElementById('run-form');        
    let computedPlan = null;

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

    const spinner = document.querySelector('.spinner-border'); // Get the spinner element
    spinner.style.display = 'block';
    const socket = new WebSocket('ws://' + window.location.host + '/ws/run/');

    socket.onopen = function(e){
        const useCache = document.getElementById('use_cache').checked;
        const message = {
            'plan': computedPlan,
            'use_cache': useCache,
        };
    socket.send(JSON.stringify(message));
    };
    
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const resultDiv = document.getElementById('results');
        resultDiv.style.overflowY = 'auto';
        resultDiv.style.height = '500px'; // Adjust height as needed

        const noResultsMessage = document.getElementById('no-results-message');
        if (noResultsMessage) {
            noResultsMessage.remove();
        }
        const resultText = document.getElementById('result-container');
        if (resultText) {
            resultText.remove();
        }


        let table = document.querySelector('#results table');
        if (!table) {
            table = document.createElement('table');
            table.classList.add('table', 'table-striped', 'mt-3');
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
        
        scrollableContainer.appendChild(table);
        resultDiv.appendChild(scrollableContainer);

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
