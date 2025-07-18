# Requirements Document

## Introduction

This document outlines the requirements for rebuilding the XOFlowers AI Agent system with a simplified, fully AI-driven approach. The system will eliminate keyword-based responses and template systems in favor of pure AI-generated responses, while maintaining the core functionality of business context, product recommendations, and security protection.

## Requirements

### Requirement 1

**User Story:** As a customer, I want to have natural conversations with the AI agent, so that I can get personalized flower recommendations and business information without feeling like I'm talking to a bot.

#### Acceptance Criteria

1. WHEN a user sends any message THEN the system SHALL use AI to understand the intent without keyword matching
2. WHEN generating responses THEN the system SHALL use AI to create natural responses without templates
3. WHEN the user asks follow-up questions THEN the system SHALL maintain conversation context using Redis
4. WHEN the conversation flows naturally THEN the system SHALL adapt responses based on previous interactions

### Requirement 2

**User Story:** As a customer, I want to receive relevant product recommendations, so that I can find the perfect flowers for my needs.

#### Acceptance Criteria

1. WHEN a user expresses interest in flowers THEN the system SHALL search ChromaDB for relevant products
2. WHEN products are found THEN the AI SHALL incorporate them naturally into the response
3. WHEN no exact matches exist THEN the system SHALL provide alternative suggestions
4. WHEN presenting products THEN the system SHALL include price, description, and personalized recommendations

### Requirement 3

**User Story:** As a customer, I want to get accurate business information, so that I can know store hours, contact details, and services.

#### Acceptance Criteria

1. WHEN a user asks business questions THEN the system SHALL access FAQ data from JSON files
2. WHEN providing business info THEN the AI SHALL present it naturally within conversation context
3. WHEN store hours are requested THEN the system SHALL provide current schedule information
4. WHEN contact information is needed THEN the system SHALL provide phone, email, and location details

### Requirement 4

**User Story:** As a business owner, I want the system to be secure from jailbreak attempts, so that the AI stays focused on flower business and maintains professional behavior.

#### Acceptance Criteria

1. WHEN a user sends a message THEN the system SHALL use AI to evaluate if the request is appropriate
2. WHEN jailbreak attempts are detected THEN the system SHALL politely redirect to flower-related topics
3. WHEN inappropriate content is identified THEN the system SHALL respond professionally while staying on topic
4. WHEN security checks pass THEN the system SHALL proceed with normal AI processing

### Requirement 5

**User Story:** As a system administrator, I want minimal Redis implementation for conversation context, so that the system can maintain conversation history efficiently.

#### Acceptance Criteria

1. WHEN a user starts a conversation THEN the system SHALL store context in Redis with user ID as key
2. WHEN processing messages THEN the system SHALL retrieve and update conversation context
3. WHEN context becomes too large THEN the system SHALL implement automatic cleanup
4. WHEN Redis is unavailable THEN the system SHALL gracefully degrade without conversation memory

### Requirement 6

**User Story:** As a developer, I want a modular system with centralized definitions, so that the codebase is maintainable and scalable.

#### Acceptance Criteria

1. WHEN system variables are needed THEN they SHALL be defined once in system_definitions.py
2. WHEN functions are created THEN they SHALL be reusable across different modules
3. WHEN the folder structure is maintained THEN each layer SHALL have clear responsibilities
4. WHEN new features are added THEN they SHALL follow the established modular pattern

### Requirement 7

**User Story:** As a system operator, I want the system to work reliably, so that customers always receive responses even during high load.

#### Acceptance Criteria

1. WHEN the system receives messages THEN it SHALL respond within 3 seconds for 95% of requests
2. WHEN OpenAI API fails THEN the system SHALL fallback to Gemini API
3. WHEN both AI services fail THEN the system SHALL provide a graceful error message
4. WHEN ChromaDB is unavailable THEN the system SHALL still provide business information from FAQ