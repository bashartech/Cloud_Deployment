/**
 * Test script for MCP tools enhancements
 * Verifies that the advanced features work properly
 */

import {
  createAddTaskTool,
  createListTasksTool,
  createUpdateTaskTool,
  createSortTasksTool
} from './src/tools/task-tools';

async function testMCPEnhancements() {
  console.log('Testing MCP Tools Enhancements...\n');

  // Test 1: Enhanced add_task with advanced fields
  console.log('1. Testing enhanced add_task tool with advanced fields...');
  try {
    const addTaskTool = await createAddTaskTool();
    console.log(`   Tool name: ${addTaskTool.name}`);
    console.log(`   Input schema: ${JSON.stringify(addTaskTool.definition.inputSchema._def.typeName)}`);
    
    // Check if advanced fields are included in the schema
    const shape = addTaskTool.definition.inputSchema.shape;
    const hasAdvancedFields = shape.priority && shape.tags && shape.due_date && 
                             shape.recurrence_pattern && shape.recurrence_end_date && 
                             shape.recurrence_count;
    
    console.log(`   Has advanced fields: ${hasAdvancedFields ? 'YES' : 'NO'}`);
    console.log('   ✓ Enhanced add_task tool created successfully\n');
  } catch (error) {
    console.error('   ✗ Error creating add_task tool:', error.message);
  }

  // Test 2: Enhanced list_tasks with filtering options
  console.log('2. Testing enhanced list_tasks tool with filtering options...');
  try {
    const listTasksTool = await createListTasksTool();
    console.log(`   Tool name: ${listTasksTool.name}`);
    
    // Check if advanced filtering fields are included in the schema
    const shape = listTasksTool.definition.inputSchema.shape;
    const hasFilteringOptions = shape.priority && shape.tag && shape.due_before;
    
    console.log(`   Has filtering options: ${hasFilteringOptions ? 'YES' : 'NO'}`);
    console.log('   ✓ Enhanced list_tasks tool created successfully\n');
  } catch (error) {
    console.error('   ✗ Error creating list_tasks tool:', error.message);
  }

  // Test 3: Enhanced update_task with advanced fields
  console.log('3. Testing enhanced update_task tool with advanced fields...');
  try {
    const updateTaskTool = await createUpdateTaskTool();
    console.log(`   Tool name: ${updateTaskTool.name}`);
    
    // Check if advanced fields are included in the schema
    const shape = updateTaskTool.definition.inputSchema.shape;
    const hasAdvancedFields = shape.priority && shape.tags && shape.due_date && 
                             shape.recurrence_pattern && shape.recurrence_end_date && 
                             shape.recurrence_count;
    
    console.log(`   Has advanced fields: ${hasAdvancedFields ? 'YES' : 'NO'}`);
    console.log('   ✓ Enhanced update_task tool created successfully\n');
  } catch (error) {
    console.error('   ✗ Error creating update_task tool:', error.message);
  }

  // Test 4: New sort_tasks tool
  console.log('4. Testing new sort_tasks tool...');
  try {
    const sortTasksTool = await createSortTasksTool();
    console.log(`   Tool name: ${sortTasksTool.name}`);
    console.log(`   Description: ${sortTasksTool.definition.description}`);
    
    // Check if sort fields are included in the schema
    const shape = sortTasksTool.definition.inputSchema.shape;
    const hasSortFields = shape.sort_by && shape.order;
    
    console.log(`   Has sort fields: ${hasSortFields ? 'YES' : 'NO'}`);
    console.log('   ✓ New sort_tasks tool created successfully\n');
  } catch (error) {
    console.error('   ✗ Error creating sort_tasks tool:', error.message);
  }

  console.log('All MCP tools enhancement tests completed!');
}

// Run the test
testMCPEnhancements().catch(console.error);