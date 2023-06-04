import React, { useState } from 'react';
import { TextField, Button, Box, Typography } from '@mui/material';

const Contact = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    message: ''
  });
  const [errors, setErrors] = useState({
    firstName: '',
    lastName: '',
    email: '',
    message: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value
    });
    setErrors({
      ...errors,
      [event.target.name]: ''
    });
    setIsSubmitted(false);
  };

  const validateForm = () => {
    let valid = true;
    const newErrors = {};

    // Validate first name
    if (formData.firstName.trim() === '') {
      newErrors.firstName = 'First name is required';
      valid = false;
    }

    // Validate last name
    if (formData.lastName.trim() === '') {
      newErrors.lastName = 'Last name is required';
      valid = false;
    }

    // Validate email format
    const emailRegex = /^\S+@\S+\.\S+$/;
    if (formData.email.trim() === '') {
      newErrors.email = 'Email is required';
      valid = false;
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Invalid email format';
      valid = false;
    }

    // Validate message
    if (formData.message.trim() === '') {
      newErrors.message = 'Message is required';
      valid = false;
    }

    setErrors(newErrors);
    return valid;
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (validateForm()) {
      // Perform form submission logic here
      console.log(formData);

      // Send form data to Django REST API
      fetch('http://127.0.0.1:8000/api/user/contact/contact/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data); // Handle the response from the API
          setIsSubmitted(true);
        })
        .catch((error) => {
          console.error(error); // Handle any errors
        });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        label="First Name"
        name="firstName"
        value={formData.firstName}
        onChange={handleChange}
        fullWidth
        margin="dense"
        error={!!errors.firstName}
        helperText={errors.firstName}
      />
      <TextField
        label="Last Name"
        name="lastName"
        value={formData.lastName}
        onChange={handleChange}
        fullWidth
        margin="dense"
        error={!!errors.lastName}
        helperText={errors.lastName}
      />
      <TextField
        label="Email"
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        fullWidth
        margin="dense"
        error={!!errors.email}
        helperText={errors.email}
      />
      <TextField
        label="Message"
        name="message"
        multiline
        rows={4}
        value={formData.message}
        onChange={handleChange}
        fullWidth
        margin="dense"
        error={!!errors.message}
        helperText={errors.message}
      />
      <Box display="flex" justifyContent="center" mt={2}>
        <Button variant="contained" color="primary" type="submit">
          Submit
        </Button>
      </Box>
      {isSubmitted && (
        <Typography variant="body1" align="center" mt={2}>
          Form submitted successfully!
        </Typography>
      )}
    </form>
  );
};

export default Contact;
