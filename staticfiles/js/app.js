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
                'execution_engine': executionEngine
            }));
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

            if (index === 0) {
                resultDiv.innerHTML += '<h3> Summary of plan: </h3> <p>' + data.plan.replace(/\n/g, '<br>') + '</p>';
                console.log("Data Plan", data.plan);
            }

            computedPlan = data.plan;

            const table = document.createElement('table');
            table.classList.add('table', 'table-striped', 'mt-3');
            const thead = table.createTHead();
            const tbody = table.createTBody();
            const headRow = thead.insertRow();

            
            const scrollableContainer = document.createElement('div');
            scrollableContainer.style.overflowX = 'auto';
            scrollableContainer.style.marginTop = '10px';

            // Assuming all records have the same structure, use the first record to get column names
            const columns = ['case_submitter_id',
                'age_at_diagnosis',
                'race',
                'ethnicity',
                'gender',
                'vital_status',
                'ajcc_pathologic_t',
                'ajcc_pathologic_n',
                'ajcc_pathologic_stage',
                'tumor_grade',
                'tumor_focality',
                'tumor_largest_dimension_diameter',
                'primary_diagnosis',
                'morphology',
                'tissue_or_organ_of_origin',
                'study'
            ];

            columns.forEach(column => {
                const th = document.createElement('th');
                th.textContent = column;
                headRow.appendChild(th);
            });

            data.records.forEach(record => {
                const row = tbody.insertRow();
                columns.forEach(column => {
                    const cell = row.insertCell();
                    cell.textContent = record[column];
                });
            });

            scrollableContainer.appendChild(table);
            resultDiv.appendChild(scrollableContainer);      

            resultDiv.innerHTML += '<p>' + data.stats + '</p>';
            index++;
        };

        socket.onclose = function(e) {
            console.error('WebSocket closed unexpectedly');
        };
    });

runForm.addEventListener('submit', function(event)){
    event.preventDefault();

    if !computedPlan {
        alert('Please compute a plan first');
        return;
    }

    const socket = new WebSocket('ws://' + window.location.host + '/ws/run/');

    socket.onopen = function(e){
        const message = {
            'plan': computedPlan
        };
    socket.send(JSON.stringify(message));
    };
    
    socket.onmessage = function(e){
        const data = JSON.parse(e.data);
        const resultDiv = document.getElementById('results');
        resultDiv.innerHTML += '<p>' + data.run_result.replace(/\n/g, '<br>') + '</p>';
    };

    socket.onclose = function(e){
        console.error('WebSocket closed unexpectedly');
    };
};
});
