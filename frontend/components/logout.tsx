"use client"
import React from 'react'
import { authClient } from '@/lib/auth-client'
import { Button } from './ui/button'
import { LogOut } from 'lucide-react'
const Logout = () => {
    const handleLogout = async () => {
        await authClient.signOut()
    }
  return (
    <div>
        <Button onClick={handleLogout}>
            Logout <LogOut className='size-4'/>
            </Button>
      
    </div>
  )
}

export default Logout
