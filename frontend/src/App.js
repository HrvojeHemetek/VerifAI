import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './styles/App.css';
import { Formik, Form, ErrorMessage, Field} from 'formik'
import { CountryDropdown } from 'react-country-region-selector'
import { TextField, Button, Alert, FormControl, FormGroup, FormLabel, FormControlLabel, Checkbox } from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import Papa from 'papaparse';
import { styled } from '@mui/material/styles';
import { DataGrid } from '@mui/x-data-grid';


const App = () => {
  const allowedExtensions = ["csv"];
  const [chekingSampleNumber, setChekingSampleNumber] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [tableRows, setTableRows] = useState([]);
  const [values, setValues] = useState([]);
  const [showQuestions, setShowQuestions] = useState(false);

  useEffect(() => {
    if (localStorage.length === 0) {
      localStorage.setItem('numOfSamples', 0);
      localStorage.setItem('country', 'Select country');
      localStorage.setItem('age', '');
      localStorage.setItem('gender', '');
      localStorage.setItem('years_of_schooling', '');
      localStorage.setItem('daily_income', '');
      localStorage.setItem('number_of_children', '');
      localStorage.setItem('work_sector', '');
      localStorage.setItem('employment', '');
      localStorage.setItem('urban_rural_living', '');
    }
  }, []);

  const navigate = useNavigate();

  const VisuallyHiddenInput = styled('input')({
    clip: 'rect(0 0 0 0)',
    clipPath: 'inset(50%)',
    height: 1,
    overflow: 'hidden',
    position: 'absolute',
    bottom: 0,
    left: 0,
    whiteSpace: 'nowrap',
    width: 1,
  });

  const handleSubmit = (valuesOfForm, setSubmitting) => {
    setSubmitting(false);

    if (!file) {
      setError("User hasn't loaded the file with questions!");
      return;
    }

    let relevant_factors = [];
    let all_factors = [];

    if (valuesOfForm.age) {
      relevant_factors.push('age');
      localStorage.setItem('age', true);
    }
    else{
      localStorage.setItem('age', '');
    }
    if (valuesOfForm.gender) {
      relevant_factors.push('gender');
      localStorage.setItem('gender', true);
    }
    else{
      localStorage.setItem('gender', '');
    }
    if (valuesOfForm.education_level) {
      relevant_factors.push('years_of_schooling');
      localStorage.setItem('years_of_schooling', true);
    }
    else{
      localStorage.setItem('years_of_schooling', '');
    }
    if (valuesOfForm.income) {
      relevant_factors.push('daily_income');
      localStorage.setItem('daily_income', true);
    }
    else{
      localStorage.setItem('daily_income', '');
    }
    if (valuesOfForm.children) {
      relevant_factors.push('number_of_children');
      localStorage.setItem('number_of_children', true);
    }
    else{
      localStorage.setItem('number_of_children', '');
    }
    if (valuesOfForm.sector) {
      relevant_factors.push('work_sector');
      localStorage.setItem('work_sector', true);
    }
    else{
      localStorage.setItem('work_sector', '');
    }
    if (valuesOfForm.unemployment_rate) {
      relevant_factors.push('employment');
      localStorage.setItem('employment', true);
    }
    else{
      localStorage.setItem('employment', '');
    }
    if (valuesOfForm.urban_population) {
      relevant_factors.push('urban_rural_living');
      localStorage.setItem('urban_rural_living', true);
    }
    else{
      localStorage.setItem('urban_rural_living', '');
    }

    localStorage.setItem('numOfSamples', valuesOfForm.numOfSamples);
    localStorage.setItem('country', valuesOfForm.country);

    all_factors.push('age');
    all_factors.push('gender');
    all_factors.push('years_of_schooling');
    all_factors.push('daily_income');
    all_factors.push('number_of_children');
    all_factors.push('work_sector');
    all_factors.push('employment');
    all_factors.push('urban_rural_living');

    navigate("/results", {state : {sentValues: valuesOfForm, file: file, relevantFactors: relevant_factors, allFactors: all_factors, questions: values}});
  }

  const handleSampleChange = (e, setFieldValue) => {
    if (Number(e.target.value) <= 0 || e.target.value === '') {   
      setChekingSampleNumber(true);
    }
    else {
      setChekingSampleNumber(false);
    }
    setFieldValue('numOfSamples', Number(e.target.value));
  }

  const handleFileChange = (e) => {
    setError("");
      if (e.target.files.length) {
          const inputFile = e.target.files[0];
          const fileExtension = inputFile?.type.split("/")[1];
          if (!allowedExtensions.includes(fileExtension)) {
              setError("User has entered an unsupported file format!");
              setFile(null);
              setShowQuestions(false);
              return;
            }
            setFile(inputFile);
            Papa.parse(inputFile, {
              header: true,
              skipEmptyLines: true,
              complete: function (results) {
                const rowsArray = [];
                const valuesArray = [];
        
                results.data.map((d) => {
                  rowsArray.push(Object.keys(d));
                  valuesArray.push(Object.values(d));
                });
                setTableRows(rowsArray[0]);
        
                setValues(valuesArray);
              },
            });
      }
      
    };

  const handleUpload = () => {
    setShowQuestions(true);
  };

  const convertTableRowsToColumns = () => {
    let columns = [];
    columns.push({field: 'id', headerName: 'Question Number', width: 300});

    for (let index = 0; index < tableRows.length; index++) {
      columns.push({field: tableRows[index], headerName: tableRows[index].charAt(0).toUpperCase() + tableRows[index].slice(1), width: 300, headerAlign: 'center', headerClassName: 'data-grid-header'});
    }

    console.log(columns);
    console.log(values);

    return columns;
  };

  const convertValuesToRows = () => {
    let rows = [];

    let columns = convertTableRowsToColumns();

    for (let indexRow = 0; indexRow < values.length; indexRow++) {
      const row = new Object();

      for (let indexColumn = 0; indexColumn < columns.length; indexColumn++) {
        if (indexColumn === 0) {
          row[columns[indexColumn].field] = indexRow + 1;
          continue;
        }
        row[columns[indexColumn].field] = values[indexRow][indexColumn - 1];
      }

      rows.push(row);
    }

    return rows;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome!</h1>
      </header>
      <div className='container'>
          <Formik 
          validate={values => {
            const errors = {};
            if (values.numOfSamples === 0 && values.country.length === 0) {
              errors.numOfSamples = 'The number of samples for AI to generate can not be zero or less!';
              errors.country = 'A specific country has to be selected!';
            }
            else if (values.country.length === 0) {
              errors.country = 'A specific country has to be selected!';
            }
            else if (chekingSampleNumber) {
              errors.numOfSamples = 'The number of samples for AI to generate can not be zero or less!';
            }
            else if (!values.age && !values.gender && !values.education_level && !values.income && !values.children && !values.sector && !values.unemployment_rate && !values.urban_population) {
              errors.checked = "At least one factor has to be selected!";
            }
            return errors;
          }}
          initialValues={{ numOfSamples: Number(localStorage.getItem('numOfSamples')), country: String(localStorage.getItem('country')),  age: Boolean(localStorage.getItem('age')), 
            gender: Boolean(localStorage.getItem('gender')), education_level: Boolean(localStorage.getItem('years_of_schooling')), 
            income: Boolean(localStorage.getItem('daily_income')), children: Boolean(localStorage.getItem('number_of_children')), 
            sector: Boolean(localStorage.getItem('work_sector')), unemployment_rate: Boolean(localStorage.getItem('employment')), 
            urban_population: Boolean(localStorage.getItem('urban_rural_living')) }}
            // validateOnMount={values => {
            //   if (localStorage.length === 0) {
            //     return true;
            //   }
            //   if (values.numOfSamples === 0 && values.country.length === 0) {
            //     return false;
            //   }
            //   if (values.country.length === 0) {
            //     return false;
            //   }
            //   if (chekingSampleNumber) {
            //     return false;
            //   }
            //   if (!values.age && !values.gender && !values.education_level && !values.income && !values.children && !values.sector && !values.unemployment_rate && !values.urban_population) {
            //     return false;
            //   }
            //   return true;
            // }}
          onSubmit={(values, {setSubmitting}) => handleSubmit(values, setSubmitting)}
          >
          {({ isSubmitting, values, setFieldValue, handleBlur, errors, isValid }) => (
            <Form className='form-container'>
              <header >
                  <h1>Choose details about your targeted demographic</h1>
              </header>
              <CountryDropdown value={values.country} onChange={(val) =>  setFieldValue('country', val === 'United States' ? 'USA' : val)} onBlur={handleBlur} defaultOptionLabel={values.country}  />
              <ErrorMessage name="country" component="div">{(msg) => <div style={{ color: "red", textAlign: "left" }}>{msg}</div>}</ErrorMessage>
              <TextField label="Input the sample size" fullWidth type="number" error={chekingSampleNumber || Boolean(errors.numOfSamples)} onChange={(e) => handleSampleChange(e, setFieldValue)} 
                helperText={errors.numOfSamples || undefined} onBlur={handleBlur} name="numOfSamples" defaultValue={values.numOfSamples} />
              <FormControl component="fieldset">
                <FormLabel component="legend">Choose relevant factors to take into consideration: </FormLabel>
                <FormGroup aria-label="position" column>
                  <FormControlLabel
                    value={values.age}
                    control={<Checkbox onChange={(e) => setFieldValue('age', e.target.checked)} checked={values.age} />}
                    label="Age"
                    labelPlacement="end"
                  />
                  <FormControlLabel
                    value={values.gender}
                    control={<Checkbox onChange={(e) => setFieldValue('gender', e.target.checked)} checked={values.gender} />}
                    label="Gender"
                    labelPlacement="end"
                  />
                  <FormControlLabel
                    value={values.education_level}
                    control={<Checkbox onChange={(e) => setFieldValue('education_level', e.target.checked)} checked={values.education_level} />}
                    label="Education Level"
                    labelPlacement="end"
                  />
                  <FormControlLabel
                    value={values.income}
                    control={<Checkbox onChange={(e) => setFieldValue('income', e.target.checked)} checked={values.income} />}
                    label="Daily Income"
                    labelPlacement="end"
                  />
                  <FormControlLabel
                    value={values.children}
                    control={<Checkbox onChange={(e) => setFieldValue('children', e.target.checked)} checked={values.children} />}
                    label="Number of Children"
                    labelPlacement="end"
                  />
                  <FormControlLabel
                    value={values.sector}
                    control={<Checkbox onChange={(e) => setFieldValue('sector', e.target.checked)} checked={values.sector} />}
                    label="Work Sector"
                    labelPlacement="end"
                  />
                  <FormControlLabel
                    value={values.unemployment_rate}
                    control={<Checkbox onChange={(e) => setFieldValue('unemployment_rate', e.target.checked)} checked={values.unemployment_rate} />}
                    label="Unemployment"
                    labelPlacement="end"
                  />
                  <FormControlLabel
                    value={values.urban_population}
                    control={<Checkbox onChange={(e) => setFieldValue('urban_population', e.target.checked)} checked={values.urban_population} />}
                    label="Urban/rural population"
                    labelPlacement="end"
                  />
                </FormGroup>
              </FormControl>
              <Button
                  fullWidth
                  component="label"
                  role={undefined}
                  variant="contained"
                  tabIndex={-1}
                  startIcon={<CloudUploadIcon />}
                >
                  Upload questions
                  <VisuallyHiddenInput type="file" onChange={handleFileChange}/>
              </Button>
              {file ? <Alert severity='success'>
                  <h2>File uploaded successfully!</h2>
                  <section>
                    File details:
                    <ul>
                      <li>Name: {file.name}</li>
                      <li>Type: {file.type}</li>
                      <li>Size: {file.size} bytes</li>
                    </ul>
                  </section>
                </Alert> : (
                  error === "User has entered an unsupported file format!" ? <Alert severity='error' onClose={() => setError("")}>{error}</Alert> : (
                    error === "User hasn't loaded the file with questions!" ? <Alert severity='error' onClose={() => setError("")}>{error}</Alert> : null
                  ) 
              )}

              {file && <button type='button' onClick={handleUpload} className='submit-button'>Show questionnaire</button>}

              <Button type="submit" fullWidth classes={'submit-button'} variant='contained' endIcon={<SendIcon />} disabled={isSubmitting || !isValid || file === null}>
                Start generating
              </Button>
            </Form>
          )}  
          </Formik>
        <div className='App-body'>

          <div style={{ marginTop: "3rem" }}>
                      {!(file && showQuestions) ? null: <DataGrid 
                                                            rows={convertValuesToRows()}
                                                            columns={convertTableRowsToColumns()}
                                                            initialState={{
                                                              pagination: {
                                                                paginationModel: { page: 0, pageSize: 5 },
                                                              },
                                                            }}
                                                            pageSizeOptions={[5, 10]}
                                                            checkboxSelection
                                                            autoHeight
                                                            rowHeight={171}
                                                          />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
