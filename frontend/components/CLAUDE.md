# Frontend Components Guidelines

## Component Structure
- `/components/auth` - Authentication-related components (AuthForm, etc.)
- `/components/task` - Task-related components (TaskItem, etc.)
- `/contexts` - React Context providers (AuthContext, etc.)

## Component Patterns
- Use TypeScript interfaces for all props
- Follow accessibility best practices (aria labels, semantic HTML)
- Use Tailwind CSS for styling
- Implement proper error boundaries for components

## Component Naming Convention
- Use PascalCase for component names
- Group related components in subdirectories
- Use descriptive names that reflect component purpose

## Component Exports
- Export components as default exports when they're the main component in a file
- Export utility functions and types as named exports

## Reusability
- Create reusable components for common UI elements
- Use composition over inheritance for component extensibility
- Consider props for customization instead of creating multiple variations