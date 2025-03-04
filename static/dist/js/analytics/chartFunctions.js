function createTopicVisualization(data, containerId = 'chart') {
    // Validate input data structure
    if (!data.completed || !data.uncovered || !data.batch_info) {
        throw new Error('Invalid data format. Required properties: completed, uncovered, batch_info');
    }

    // Get unique batch IDs from the data
    const batches = Array.from(new Set([
        ...data.completed.map(obj => Object.keys(obj)[0]),
        ...data.uncovered.map(obj => Object.keys(obj)[0])
    ]));

    const coveredCounts = [];
    const uncoveredCounts = [];
    const coveredTopics = [];
    const uncoveredTopics = [];
    const subjects = [];

    // Process data for each batch
    batches.forEach(batchId => {
        const covered = data.completed.find(obj => obj[batchId])?.[batchId] || [];
        const uncovered = data.uncovered.find(obj => obj[batchId])?.[batchId] || [];
        const batchInfo = data.batch_info.find(obj => obj[batchId])?.[batchId];
        
        if (!batchInfo) {
            throw new Error(`Batch info not found for batch ${batchId}`);
        }

        coveredCounts.push(covered.length);
        uncoveredCounts.push(uncovered.length);
        
        // Format topics with HTML line breaks and bullets
        const formattedCovered = covered.map(topic => `• ${topic}`).join('<br>');
        const formattedUncovered = uncovered.map(topic => `• ${topic}`).join('<br>');
        
        coveredTopics.push(formattedCovered);
        uncoveredTopics.push(formattedUncovered);
        subjects.push(`${batchInfo.subject} (${batchId})`);
    });

    // Create traces for the visualization
    const coveredTrace = {
        x: subjects,
        y: coveredCounts,
        name: 'Covered Topics',
        type: 'bar',
        text: coveredTopics,
        textposition: 'none',
        hovertemplate: 
            '<span style="font-size: 14px;"><b>Covered Topics:</b><br>%{text}</span>' +
            "<extra></extra>",
        marker: { color: 'rgba(56, 165, 89, 0.7)' },
        width: 0.3
    };

    const uncoveredTrace = {
        x: subjects,
        y: uncoveredCounts,
        name: 'Uncovered Topics',
        type: 'bar',
        text: uncoveredTopics,
        textposition: 'none',
        hovertemplate: 
            '<span style="font-size: 14px;"><b>Uncovered Topics:</b><br>%{text}</span>' +
            "<extra></extra>",
        marker: { color: 'rgba(219, 64, 82, 0.7)' },
        width: 0.3
    };

    const layout = {
        title: 'Covered vs Uncovered Topics',
        barmode: 'stack',
        xaxis: { title: 'Subject (Batch ID)', tickangle: 45 },
        yaxis: { title: 'Number of Topics' },
        hovermode: 'closest',
        hoverlabel: {
            bgcolor: 'white',
            bordercolor: '#666',
            font: { size: 14 },
            align: 'left'
        }
    };

    // Create the plot
    Plotly.newPlot(containerId, [coveredTrace, uncoveredTrace], layout);
}




function createStudentSessionChart(batchId, data, containerId) {
    // Extract relevant data for the given batch
    const batchData = data.batch_data[batchId];
    const batchInfo = data.batch_info.find(info => info[batchId]);
    const studentData = batchInfo[batchId].student_data;

    // Prepare a mapping of student enrollments to names
    const studentMap = studentData.reduce((map, student) => {
        map[student.enrol] = student.name;
        return map;
    }, {});

    // Count sessions attended by each student
    const studentSessionCounts = {};
    batchData.forEach(entry => {
        entry.sessions.forEach(session => {
            session.students.forEach(studentId => {
                if (!studentSessionCounts[studentId]) {
                    studentSessionCounts[studentId] = 0;
                }
                studentSessionCounts[studentId]++;
            });
        });
    });

    // Prepare data for the chart
    const xAxis = Object.keys(studentSessionCounts).map(enrol => studentMap[enrol] || "Unknown Student");
    const yAxis = Object.values(studentSessionCounts);

    // Create a bar chart
    const chartData = [{
        type: 'bar',
        x: xAxis,
        y: yAxis,
        text: yAxis.map(count => `${count} sessions`),
        textposition: 'auto',
        hoverinfo: 'x+y',
        marker: {
            color: 'rgb(0, 123, 255)'
        },
        width:0.3
    }];

    const layout = {
        title: `Sessions Attended by Students in Batch ${batchId}`,
        xaxis: {
            title: 'Student Names',
            // tickangle:  // Rotate names for better readability
        },
        yaxis: {
            title: 'Number of Sessions Attended'
        }
    };

    Plotly.newPlot(containerId, chartData, layout);
}
