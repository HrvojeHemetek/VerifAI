import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Plot from 'react-plotly.js';
import '../styles/Results.css';
import { Button } from '@mui/material';

const Results = () => {
    const location = useLocation();
    const [data, setData] = useState([]);

    useEffect(() => {
            const controller = new AbortController();
            const run = async (controller) => {   

                var form_data = new FormData();
                form_data.append('file', location.state.file);
                form_data.append('sample_size', location.state.sentValues.numOfSamples);
                form_data.append('relevant_factors', JSON.stringify(location.state.relevantFactors));
                form_data.append('country', location.state.sentValues.country);

                let response;
                try {

                    response = await fetch('http://localhost:8000/survey/', {
                        method: 'POST', 
                        body: form_data
                    });
                
                } catch (error) {
                    if (error.name === "AbortError") {
                        return;
                    }
                }
                
                const reader = response.body.getReader();
                const chunks = [];
                
                let done, value;
                const dec = new TextDecoder();

                while (!done) {
                ({ value, done } = await reader.read());
                if (done) {
                    return chunks;
                }
                const strval = dec.decode(value, { stream: true });
                chunks.push(strval);
                setData(data => [...data, {index: chunks.length - 1, value: chunks[chunks.length - 1]}]);
                }
            }
            run(controller);

            return () => controller.abort();

    }, []);

    const navigate = useNavigate();

    const getData = (factor) => {
        const jsonDataSample = JSON.parse(data[0].value.replace(/'/g, '"').replace(/None/g, '"None"').replace(/nan/g, '"None"'));

        const jsonDataPopulation = JSON.parse(data[1].value.replace(/'/g, '"').replace(/None/g, '"None"').replace(/nan/g, '"None"'));

        for (const [key, value] of Object.entries(jsonDataSample)) {
            if (key === factor) {

                if (Object.entries(value).length === 0) {
                    return [{x: [1], y: [value], name: 'Sample', type: 'bar'}, {x: [2], y: [Object.entries(jsonDataPopulation).find((value) => value[0] === key)[1]], name: 'Population', type: 'bar'}];
                }

                let dataSample = [];
                let dataPopulation = [];
                let labels = [];

                for (const [keyNextDepth, valueNextDepth] of Object.entries(value)) {
                    if (Object.entries(valueNextDepth).length === 0 && valueNextDepth !== 'None') {
                        if (Object.entries(jsonDataPopulation).find((value) => value[0] === key)[1] === 'None') {
                            dataSample.push(valueNextDepth);
                            dataPopulation.push(0);
                            labels.push(keyNextDepth);
                        }
                        else {
                            dataSample.push(valueNextDepth);
                            dataPopulation.push(Object.entries(Object.entries(jsonDataPopulation).find((value) => value[0] === key)[1]).find((value) => value[0] === keyNextDepth)[1]);
                            labels.push(keyNextDepth);
                        }
                    }
                    else if (valueNextDepth !== 'None') {
                        for (const [finalKey, finalValue] of Object.entries(valueNextDepth)) {
                            dataSample.push(finalValue);
                            dataPopulation.push(Object.entries(Object.entries(Object.entries(jsonDataPopulation).find((value) => value[0] === key)[1]).
                                                    find((value) => value[0] === keyNextDepth)[1]).find((value) => value[0] === finalKey)[1]);
                            labels.push(keyNextDepth + ' - ' + beautifyFactorName(finalKey));
                        }
                    }
                }

                return [{x: labels, y: dataSample, name: 'Sample', type: 'bar'}, {x: labels, y: dataPopulation, name: 'Population', type: 'bar'}];

            }
        }
    };

    const beautifyFactorName = (factor) => {
        let name = '';

        function capitalizeFirstLetter(string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        }

        factor.split('_').forEach((value, index, values) => {
            if (index === 0) {
                name = capitalizeFirstLetter(value);
            }
            else {
                name = name + ' ' + capitalizeFirstLetter(value);
            }
        });
        return name;
    };

    const getQuestionData = (question) => {
        const jsonDataquestions = JSON.parse(data[2].value.replace(/'/g, '"').replace(/None/g, '"None"').replace(/nan/g, '"None"'));
        
        for (const [key, value] of Object.entries(jsonDataquestions)) {
            if (key.includes(question[0])) {

                let labels = [];
                let data = [];

                for (const [keyNextDepth, valueNextDepth] of Object.entries(value)) {
                    labels.push(keyNextDepth);
                    data.push(valueNextDepth);
                }

                return [{x: labels, y: data.map((value, index, array) => {
                    return value / location.state.sentValues.numOfSamples;                    
                }), type: 'bar'}];
            }
        }
    };

    return (
        <div className="grid-container">
            <div className="header">
                Results
                <Button
                  fullWidth
                  component="label"
                  role={undefined}
                  variant="contained"
                  tabIndex={-1}
                  onClick={() => navigate("/")}
                >
                  Go the front page
              </Button>
            </div>
            <div className="left-column">
                <h2>Demographic data</h2>
                {data.length > 1 ? location.state.relevantFactors.map((factor, index, factors) =>  {return (<div key={index}>
                    <Plot
                        data={getData(factor)}
                        layout={ {width: 500, height: 500, title: factor === 'employment' ? 'Unemployment rate' : beautifyFactorName(factor), barmode: 'group'} }
                    />
                </div>);}) : null}
            </div>
            <div className="right-column">
                <h2>Data from questions</h2>
                {data.length > 2 ? location.state.questions.map((question, index, questions) => {
                    return (<div key={index}>
                        <Plot
                            data={getQuestionData(question)}
                            layout={ {width: 500, height: 500, title: question[0], barmode: 'group', yaxis: {
                                tickformat: ',.0%',
                                range: [0,1]
                              }} }
                        />
                    </div>)
                }) : null}
            </div>
        </div>
    );
}

export default Results;