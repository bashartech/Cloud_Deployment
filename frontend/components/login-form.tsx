
"use client"

import type React from "react"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { z } from "zod"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { Loader2 } from "lucide-react"
import { authClient } from "@/lib/auth-client"

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

export function LoginForm({ className, ...props }: React.ComponentPropsWithoutRef<"div">) {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  })

  const signInWithGoogle = async () => {
    try {
      const result = await authClient.signIn.social({
        provider: "google",
        callbackURL: "/dashboard",  // Use callbackURL as per Better Auth API
      });
      
      // If there's an error, handle it
      if (result.error) {
        toast.error(result.error.message || "Google sign-in failed");
        return;
      }
      
      // If successful, the redirect should happen automatically
      // But if it doesn't, manually redirect after a short delay
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 1000);
    } catch (error) {
      toast.error("Google sign-in failed. Please try again.");
    }
  }

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true)
    try {
      const result = await authClient.signIn.email({
        email: values.email,
        password: values.password,
        callbackURL: "/dashboard",  // Use callbackURL as per Better Auth API
      });

      if (result.error) {
        toast.error(result.error.message || "Login failed");
      } else {
        toast.success("Sign in successful!");
        // Wait a moment for session to establish, then redirect
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 500);
      }
    } catch (error) {
      toast.error("Login failed. Please try again.");
    }
    setIsLoading(false)
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="bg-gradient-to-b from-neutral-900 to-black border-neutral-800/50 shadow-2xl">
        <CardHeader className="text-center space-y-3 pb-6">
          <div className="flex justify-center mb-2">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
              <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
            Welcome Back
          </CardTitle>
          <CardDescription className="text-gray-400">Sign in to your account to continue</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid gap-4">
                <Button
                  variant="outline"
                  className="w-full bg-neutral-800/50 hover:bg-neutral-700/50 border-neutral-700 text-white transition-all duration-300 hover:scale-105"
                  onClick={signInWithGoogle}
                  type="button"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" className="w-4 h-4 mr-2">
                    <path
                      d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
                      fill="currentColor"
                    />
                  </svg>
                  Continue with Google
                </Button>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-neutral-700"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-gradient-to-b from-neutral-900 to-black text-gray-400">
                    Or continue with email
                  </span>
                </div>
              </div>

              <div className="grid gap-4">
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-gray-300">Email Address</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="your@email.com"
                          className="bg-neutral-800/50 border-neutral-700 text-white placeholder:text-gray-500 focus:border-blue-500 focus:ring-blue-500/20 transition-all duration-300"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <div className="flex items-center justify-between">
                        <FormLabel className="text-gray-300">Password</FormLabel>
                        <a href="#" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                          Forgot?
                        </a>
                      </div>
                      <FormControl>
                        <Input
                          placeholder="••••••••"
                          type="password"
                          className="bg-neutral-800/50 border-neutral-700 text-white placeholder:text-gray-500 focus:border-blue-500 focus:ring-blue-500/20 transition-all duration-300"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold transition-all duration-300 hover:scale-105 disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="animate-spin h-4 w-4 mr-2" />
                      Signing in...
                    </>
                  ) : (
                    "Sign In"
                  )}
                </Button>
              </div>

              <div className="text-center text-sm text-gray-400">
                Don&apos;t have an account?{" "}
                <a href="/signup" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors">
                  Create one
                </a>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>

      <div className="text-balance text-center text-xs text-gray-500">
        By continuing, you agree to our{" "}
        <a href="#" className="text-gray-400 hover:text-gray-300 transition-colors">
          Terms of Service
        </a>{" "}
        and{" "}
        <a href="#" className="text-gray-400 hover:text-gray-300 transition-colors">
          Privacy Policy
        </a>
      </div>
    </div>
  )
}
