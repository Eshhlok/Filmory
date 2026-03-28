"use client"

import { useState } from "react"
import { MessageSquare, Star, Send, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function submitFeedback(rating: number, feedback: string): Promise<void> {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating, feedback }),
  })
  if (!res.ok) throw new Error("Failed to submit feedback")
}

export function FeedbackButton() {
  const [rating, setRating]             = useState(0)
  const [hoveredRating, setHoveredRating] = useState(0)
  const [feedback, setFeedback]         = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted]   = useState(false)
  const [isOpen, setIsOpen]             = useState(false)

  const handleSubmit = async () => {
    if (rating === 0) return
    setIsSubmitting(true)
    try {
      await submitFeedback(rating, feedback)
      setIsSubmitted(true)
      setTimeout(() => {
        setIsOpen(false)
        setTimeout(() => {
          setRating(0)
          setFeedback("")
          setIsSubmitted(false)
        }, 300)
      }, 2000)
    } catch (error) {
      console.error("Failed to submit feedback:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const ratingLabels = ["Poor", "Fair", "Good", "Very Good", "Excellent"]
  const activeRating = hoveredRating || rating

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {/* ✅ Amber floating button matching Filmory theme */}
        <button
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-5 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-full shadow-lg shadow-amber-600/30 hover:shadow-xl hover:shadow-amber-600/40 transition-all duration-300 hover:scale-105 cursor-pointer"
        >
          <MessageSquare className="w-5 h-5" />
          <span className="hidden sm:inline text-sm font-medium">Feedback</span>
        </button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md bg-stone-50 border-stone-200">
        {!isSubmitted ? (
          <>
            <DialogHeader className="text-center sm:text-center">
              {/* ✅ Amber icon background */}
              <div className="mx-auto mb-2 flex w-12 h-12 items-center justify-center rounded-full bg-amber-100">
                <Sparkles className="w-6 h-6 text-amber-600" />
              </div>
              <DialogTitle className="text-xl font-serif text-stone-800">
                Rate Your Experience
              </DialogTitle>
              <DialogDescription className="text-stone-500">
                Help us improve Filmory by sharing your thoughts
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-4">
              {/* Star Rating */}
              <div className="flex flex-col items-center gap-3">
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setRating(star)}
                      onMouseEnter={() => setHoveredRating(star)}
                      onMouseLeave={() => setHoveredRating(0)}
                      className="p-1 transition-transform duration-200 hover:scale-110 focus:outline-none rounded-sm cursor-pointer"
                    >
                      <Star
                        className={cn(
                          "w-9 h-9 transition-all duration-200",
                          activeRating >= star
                            ? "fill-amber-500 text-amber-500 drop-shadow-[0_0_8px_rgba(245,158,11,0.6)]"
                            : "text-stone-300 hover:text-stone-400"
                        )}
                      />
                    </button>
                  ))}
                </div>
                {/* Rating label */}
                <p className={cn(
                  "h-5 text-sm font-medium text-amber-600 transition-opacity duration-200",
                  activeRating > 0 ? "opacity-100" : "opacity-0"
                )}>
                  {ratingLabels[activeRating - 1]}
                </p>
              </div>

              {/* Feedback Textarea */}
              <div className="space-y-2">
                <label htmlFor="feedback" className="text-sm font-medium text-stone-700">
                  Your Feedback{" "}
                  <span className="text-stone-400">(optional)</span>
                </label>
                <Textarea
                  id="feedback"
                  placeholder="Tell us what you think about Filmory..."
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  className="min-h-24 resize-none bg-white border-stone-200 focus:border-amber-400 focus:ring-amber-400/20 text-stone-800 placeholder:text-stone-400"
                  rows={4}
                />
              </div>

              {/* Submit Button */}
              <button
                onClick={handleSubmit}
                disabled={rating === 0 || isSubmitting}
                className="w-full flex items-center justify-center gap-2 py-3 bg-amber-600 hover:bg-amber-700 disabled:bg-stone-200 disabled:text-stone-400 text-white font-medium rounded-xl transition-all duration-200 cursor-pointer disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Submit Feedback
                  </>
                )}
              </button>
            </div>
          </>
        ) : (
          /* Success state */
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="mb-4 flex w-16 h-16 items-center justify-center rounded-full bg-amber-100 animate-in zoom-in-50 duration-300">
              <Sparkles className="w-8 h-8 text-amber-600" />
            </div>
            <h3 className="font-serif text-xl text-stone-800 mb-2 animate-in fade-in-0 slide-in-from-bottom-2 duration-300 delay-100">
              Thank You!
            </h3>
            <p className="text-stone-500 animate-in fade-in-0 slide-in-from-bottom-2 duration-300 delay-200">
              Your feedback helps us make Filmory better for everyone.
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
